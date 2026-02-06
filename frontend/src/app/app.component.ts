import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import {
  BehaviorSubject,
  catchError,
  combineLatest,
  map,
  of,
  shareReplay,
  switchMap
} from 'rxjs';

interface ReportTask {
  category: string;
  task: string;
  score: number;
  n_questions: number;
}

interface ReportCategory {
  score: number;
  tasks: Record<string, { score: number; n_questions: number }>;
  n_tasks: number;
}

interface Report {
  overall: number;
  categories: Record<string, ReportCategory>;
  tasks: Record<string, ReportTask>;
  n_questions: number;
  n_missing: number;
}

interface Turn {
  role: string;
  content: string;
}

interface Question {
  question_id: string;
  category: string;
  task: string;
  turns: Turn[];
  answer_type: string;
  ground_truth: unknown;
  release_date: string;
  license: string;
  attribution: string;
}

interface AutocompleteOption {
  letter: string;
  text: string;
}

interface QuestionSuggestion {
  id: string;
  category: string;
  task: string;
  answerType: string;
  title: string;
  options: AutocompleteOption[];
  instruction: string;
  details: string[];
  holidayDates: string[];
  fullPrompt: string;
  haystack: string;
}

interface CategoryView {
  name: string;
  score: number;
  nTasks: number;
  tasks: Array<{ name: string; score: number; nQuestions: number }>;
}

interface QuestionView {
  id: string;
  prompt: string;
  category: string;
  task: string;
  answerType: string;
}

interface LeaderboardRow {
  name: string;
  subtitle: string;
  overall: number;
  categoryScores: Record<string, number>;
}

interface ViewModel {
  releaseId: string;
  releaseDate: string;
  bibtex: string;
  overall: number;
  nQuestions: number;
  nMissing: number;
  categoryCount: number;
  taskCount: number;
  categories: CategoryView[];
  categoryHeaders: string[];
  leaderboardRows: LeaderboardRow[];
  sampleQuestions: QuestionView[];
  licenses: string[];
  attributions: string[];
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  readonly releaseDates = ['2026-02-05', '2026-02-06'];
  selectedReleaseIndex = 0;

  searchQuery = '';
  autocompleteOpen = false;
  activeSuggestionIndex = -1;
  suggestions: QuestionSuggestion[] = [];

  private searchIndex: QuestionSuggestion[] = [];
  private blurTimer: ReturnType<typeof setTimeout> | null = null;
  private holidayDateLookup: Record<string, string> = {};
  private hebrewPartsFormatter: Intl.DateTimeFormat | null = null;
  private hebrewPartsFormatterInitialized = false;

  private readonly releaseIndex$ = new BehaviorSubject<number>(0);
  private readonly releaseId$ = this.releaseIndex$.pipe(
    map((index) => this.releaseDates[index])
  );

  private readonly report$ = this.http
    .get<Report>('assets/results.sample.json')
    .pipe(shareReplay(1));

  private readonly questions$ = this.releaseId$.pipe(
    switchMap((releaseId) =>
      this.http.get(`assets/releases/${releaseId}/questions.jsonl`, {
        responseType: 'text'
      })
    ),
    map((text) => this.parseJsonl(text)),
    shareReplay(1)
  );

  readonly vm$ = combineLatest([
    this.report$,
    this.questions$,
    this.releaseId$
  ]).pipe(
    map(([report, questions, releaseId]) =>
      this.buildViewModel(report, questions, releaseId)
    ),
    catchError((error) => {
      console.error('Failed to load benchmark assets', error);
      return of<ViewModel | null>(null);
    })
  );

  constructor(private readonly http: HttpClient) {
    this.holidayDateLookup = this.computeHolidayDateLookup(new Date());

    this.questions$
      .pipe(
        catchError((error) => {
          console.error('Failed to build question index', error);
          return of([] as Question[]);
        })
      )
      .subscribe((questions) => {
        this.searchIndex = questions.map((question) => this.indexQuestion(question));
        this.updateSuggestions();
      });
  }

  get sliderPercent(): number {
    if (this.releaseDates.length <= 1) {
      return 50;
    }
    return (this.selectedReleaseIndex / (this.releaseDates.length - 1)) * 100;
  }

  onReleaseChange(event: Event): void {
    const target = event.target as HTMLInputElement;
    const value = Number.parseInt(target.value, 10);
    if (Number.isNaN(value)) {
      return;
    }

    this.selectedReleaseIndex = value;
    this.releaseIndex$.next(value);

    // Avoid briefly showing stale results from the previous release.
    this.activeSuggestionIndex = -1;
    this.suggestions = [];
  }

  get showAutocomplete(): boolean {
    return this.autocompleteOpen && this.searchQuery.trim().length > 0;
  }

  onSearchInput(event: Event): void {
    const target = event.target as HTMLInputElement;
    this.searchQuery = target.value;
    this.autocompleteOpen = true;
    this.activeSuggestionIndex = -1;
    this.updateSuggestions();
  }

  onSearchFocus(): void {
    if (this.blurTimer) {
      clearTimeout(this.blurTimer);
      this.blurTimer = null;
    }
    this.autocompleteOpen = true;
    this.updateSuggestions();
  }

  onSearchBlur(): void {
    if (this.blurTimer) {
      clearTimeout(this.blurTimer);
    }
    this.blurTimer = setTimeout(() => {
      this.autocompleteOpen = false;
      this.activeSuggestionIndex = -1;
    }, 80);
  }

  clearSearch(event?: Event): void {
    event?.preventDefault();
    this.searchQuery = '';
    this.autocompleteOpen = false;
    this.activeSuggestionIndex = -1;
    this.suggestions = [];
  }

  selectSuggestion(suggestion: QuestionSuggestion, event?: Event): void {
    event?.preventDefault();
    this.searchQuery = suggestion.id;
    this.autocompleteOpen = false;
    this.activeSuggestionIndex = -1;
    this.suggestions = [];
  }

  onSearchKeydown(event: KeyboardEvent): void {
    if (!this.showAutocomplete) {
      if (event.key === 'Escape') {
        this.autocompleteOpen = false;
        this.activeSuggestionIndex = -1;
      }
      return;
    }

    if (event.key === 'ArrowDown') {
      event.preventDefault();
      if (this.suggestions.length === 0) {
        return;
      }
      this.activeSuggestionIndex =
        this.activeSuggestionIndex < 0
          ? 0
          : Math.min(this.activeSuggestionIndex + 1, this.suggestions.length - 1);
      return;
    }

    if (event.key === 'ArrowUp') {
      event.preventDefault();
      if (this.suggestions.length === 0) {
        return;
      }
      this.activeSuggestionIndex =
        this.activeSuggestionIndex < 0
          ? this.suggestions.length - 1
          : Math.max(this.activeSuggestionIndex - 1, 0);
      return;
    }

    if (event.key === 'Enter') {
      if (this.activeSuggestionIndex >= 0) {
        event.preventDefault();
        const selected = this.suggestions[this.activeSuggestionIndex];
        if (selected) {
          this.selectSuggestion(selected);
        }
      }
      return;
    }

    if (event.key === 'Escape') {
      this.autocompleteOpen = false;
      this.activeSuggestionIndex = -1;
    }
  }

  private parseJsonl(text: string): Question[] {
    return text
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter((line) => line.length > 0)
      .map((line) => JSON.parse(line) as Question);
  }

  private indexQuestion(question: Question): QuestionSuggestion {
    const fullPrompt = question.turns?.[0]?.content ?? '';
    const preview = this.buildPromptPreview(fullPrompt);
    const holidayDates = this.getHolidayDatesForPrompt(fullPrompt);
    const haystack = `${question.question_id} ${question.category} ${question.task} ${question.answer_type} ${fullPrompt}`
      .toLowerCase()
      .replace(/\s+/g, ' ')
      .trim();

    return {
      id: question.question_id,
      category: question.category,
      task: question.task,
      answerType: question.answer_type,
      title: preview.title,
      options: preview.options,
      instruction: preview.instruction,
      details: preview.details,
      holidayDates,
      fullPrompt,
      haystack
    };
  }

  private getHolidayDatesForPrompt(prompt: string): string[] {
    const text = prompt.toLowerCase();
    const lines: string[] = [];

    const add = (key: string) => {
      const value = this.holidayDateLookup[key];
      if (!value) {
        return;
      }
      if (!lines.includes(value)) {
        lines.push(value);
      }
    };

    if (text.includes('erev pesach')) {
      add('erev_pesach');
      add('pesach');
    } else if (text.includes('pesach')) {
      add('pesach');
    }

    if (text.includes('purim')) {
      add('purim');
      if (text.includes('shushan') || text.includes('jerusalem') || text.includes('15 adar')) {
        add('shushan_purim');
      }
    }

    if (text.includes('rosh chodesh')) {
      add('rosh_chodesh');
    }

    if (text.includes('shavuot') || text.includes('shavuos')) {
      add('shavuos');
    }

    if (text.includes('yom kippur')) {
      add('yom_kippur');
    }

    if (text.includes('rosh hashana') || text.includes('rosh hashanah')) {
      add('rosh_hashana');
    }

    if (text.includes('sukkot') || text.includes('sukkos')) {
      add('sukkos');
    }

    if (text.includes('chanukah') || text.includes('hanukkah')) {
      add('chanukah');
    }

    return lines;
  }

  private computeHolidayDateLookup(anchor: Date): Record<string, string> {
    const lookup: Record<string, string> = {};

    const formatMd = new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric'
    });
    const formatMdy = new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });

    const formatRange = (start: Date, end: Date) => {
      const startYear = start.getFullYear();
      const endYear = end.getFullYear();
      if (startYear === endYear) {
        return `${formatMd.format(start)} - ${formatMd.format(end)}, ${startYear}`;
      }
      return `${formatMdy.format(start)} - ${formatMdy.format(end)}`;
    };

    const formatOne = (date: Date) => formatMdy.format(date);

    const purim = this.findNextHebrewDate(anchor, (h) => {
      const month = h.month.toLowerCase();
      return h.day === 14 && month.startsWith('adar') && month !== 'adar i';
    });
    if (purim) {
      lookup['purim'] = `Purim: ${formatOne(purim)}`;
    }

    const shushanPurim = this.findNextHebrewDate(anchor, (h) => {
      const month = h.month.toLowerCase();
      return h.day === 15 && month.startsWith('adar') && month !== 'adar i';
    });
    if (shushanPurim) {
      lookup['shushan_purim'] = `Shushan Purim: ${formatOne(shushanPurim)}`;
    }

    const erevPesach = this.findNextHebrewDate(anchor, (h) => h.day === 14 && h.month.toLowerCase() === 'nisan');
    if (erevPesach) {
      lookup['erev_pesach'] = `Erev Pesach: ${formatOne(erevPesach)}`;
    }

    const pesachStart = this.findNextHebrewDate(anchor, (h) => h.day === 15 && h.month.toLowerCase() === 'nisan');
    if (pesachStart) {
      const pesachEnd = this.addDays(pesachStart, 7);
      lookup['pesach'] = `Pesach: ${formatRange(pesachStart, pesachEnd)}`;
    }

    const shavuosStart = this.findNextHebrewDate(anchor, (h) => h.day === 6 && h.month.toLowerCase() === 'sivan');
    if (shavuosStart) {
      const shavuosEnd = this.addDays(shavuosStart, 1);
      lookup['shavuos'] = `Shavuos: ${formatRange(shavuosStart, shavuosEnd)}`;
    }

    const rhStart = this.findNextHebrewDate(anchor, (h) => h.day === 1 && h.month.toLowerCase() === 'tishrei');
    if (rhStart) {
      const rhEnd = this.addDays(rhStart, 1);
      lookup['rosh_hashana'] = `Rosh Hashana: ${formatRange(rhStart, rhEnd)}`;
    }

    const yk = this.findNextHebrewDate(anchor, (h) => h.day === 10 && h.month.toLowerCase() === 'tishrei');
    if (yk) {
      lookup['yom_kippur'] = `Yom Kippur: ${formatOne(yk)}`;
    }

    const sukkosStart = this.findNextHebrewDate(anchor, (h) => h.day === 15 && h.month.toLowerCase() === 'tishrei');
    if (sukkosStart) {
      const sukkosEnd = this.addDays(sukkosStart, 8);
      lookup['sukkos'] = `Sukkos: ${formatRange(sukkosStart, sukkosEnd)}`;
    }

    const chanukahStart = this.findNextHebrewDate(anchor, (h) => h.day === 25 && h.month.toLowerCase() === 'kislev');
    if (chanukahStart) {
      const chanukahEnd = this.addDays(chanukahStart, 7);
      lookup['chanukah'] = `Chanukah: ${formatRange(chanukahStart, chanukahEnd)}`;
    }

    const roshChodesh = this.findNextHebrewDate(anchor, (h) => h.day === 1);
    if (roshChodesh) {
      const parts = this.getHebrewParts(roshChodesh);
      const labelMonth = parts?.month ?? 'Rosh Chodesh';
      const prev = this.addDays(roshChodesh, -1);
      const prevParts = this.getHebrewParts(prev);
      if (prevParts?.day === 30) {
        lookup['rosh_chodesh'] = `Rosh Chodesh ${labelMonth}: ${formatRange(prev, roshChodesh)}`;
      } else {
        lookup['rosh_chodesh'] = `Rosh Chodesh ${labelMonth}: ${formatOne(roshChodesh)}`;
      }
    }

    return lookup;
  }

  private findNextHebrewDate(
    anchor: Date,
    match: (parts: { day: number; month: string; year: number }) => boolean
  ): Date | null {
    const maxDays = 700;
    const d = new Date(anchor);
    d.setHours(12, 0, 0, 0);

    for (let i = 0; i <= maxDays; i += 1) {
      const parts = this.getHebrewParts(d);
      if (parts && match(parts)) {
        return new Date(d);
      }
      d.setDate(d.getDate() + 1);
    }

    return null;
  }

  private addDays(date: Date, delta: number): Date {
    const next = new Date(date);
    next.setDate(next.getDate() + delta);
    return next;
  }

  private getHebrewParts(date: Date): { day: number; month: string; year: number } | null {
    if (!this.hebrewPartsFormatterInitialized) {
      this.hebrewPartsFormatterInitialized = true;
      try {
        this.hebrewPartsFormatter = new Intl.DateTimeFormat('en-u-ca-hebrew', {
          day: 'numeric',
          month: 'long',
          year: 'numeric'
        });
      } catch {
        this.hebrewPartsFormatter = null;
      }
    }

    if (!this.hebrewPartsFormatter) {
      return null;
    }

    try {
      const parts = this.hebrewPartsFormatter.formatToParts(date);

      let day: number | undefined;
      let month: string | undefined;
      let year: number | undefined;

      for (const part of parts) {
        if (part.type === 'day') {
          day = Number(part.value);
        } else if (part.type === 'month') {
          month = part.value;
        } else if (part.type === 'year') {
          year = Number(part.value);
        }
      }

      if (!day || !month || !year) {
        return null;
      }

      return { day, month, year };
    } catch {
      return null;
    }
  }

  private buildPromptPreview(prompt: string): {
    title: string;
    options: AutocompleteOption[];
    instruction: string;
    details: string[];
  } {
    const rawLines = prompt.split(/\r?\n/);
    const lines = this.stripLeadingBenchmarkBlurb(rawLines)
      .map((line) => line.trim())
      .filter((line) => line.length > 0);

    const title = lines[0] ?? 'Untitled question';

    const options: AutocompleteOption[] = [];
    const details: string[] = [];
    let instruction = '';

    for (const line of lines.slice(1)) {
      const match = line.match(/^([ABCD])\.\s+(.*)$/);
      if (match) {
        options.push({ letter: match[1], text: match[2] });
        continue;
      }

      const lowered = line.toLowerCase();
      if (lowered.startsWith('answer') || lowered.startsWith('return')) {
        instruction = line;
        continue;
      }

      details.push(line);
    }

    return { title, options, instruction, details: details.slice(0, 4) };
  }

  private stripLeadingBenchmarkBlurb(lines: string[]): string[] {
    let idx = 0;
    while (idx < lines.length && lines[idx].trim().length === 0) {
      idx += 1;
    }

    const first = (lines[idx] ?? '').trim().toLowerCase();
    if (
      first.startsWith('global assumptions') ||
      first.startsWith('lens definitions')
    ) {
      while (idx < lines.length && lines[idx].trim().length !== 0) {
        idx += 1;
      }
      while (idx < lines.length && lines[idx].trim().length === 0) {
        idx += 1;
      }
    }

    return lines.slice(idx);
  }

  private updateSuggestions(): void {
    if (!this.autocompleteOpen) {
      this.suggestions = [];
      return;
    }

    const query = this.searchQuery.trim().toLowerCase();
    if (query.length < 2) {
      this.suggestions = [];
      return;
    }

    const terms = query.split(/\s+/).filter(Boolean);
    const matches: Array<{ suggestion: QuestionSuggestion; score: number }> = [];

    for (const suggestion of this.searchIndex) {
      if (!terms.every((term) => suggestion.haystack.includes(term))) {
        continue;
      }
      matches.push({
        suggestion,
        score: this.scoreSuggestion(query, suggestion)
      });
    }

    matches.sort((a, b) => a.score - b.score);
    this.suggestions = matches.slice(0, 8).map((match) => match.suggestion);

    if (this.activeSuggestionIndex >= this.suggestions.length) {
      this.activeSuggestionIndex = this.suggestions.length ? 0 : -1;
    }
  }

  private scoreSuggestion(query: string, suggestion: QuestionSuggestion): number {
    const id = suggestion.id.toLowerCase();
    const category = suggestion.category.toLowerCase();
    const task = suggestion.task.toLowerCase();
    const title = suggestion.title.toLowerCase();

    if (id.startsWith(query)) {
      return 0;
    }
    if (id.includes(query)) {
      return 1 + id.indexOf(query) / 1000;
    }
    if (task.startsWith(query)) {
      return 2;
    }
    if (task.includes(query)) {
      return 3 + task.indexOf(query) / 1000;
    }
    if (category.includes(query)) {
      return 4 + category.indexOf(query) / 1000;
    }
    if (title.includes(query)) {
      return 5 + title.indexOf(query) / 1000;
    }
    return 10;
  }

  private buildViewModel(
    report: Report,
    questions: Question[],
    releaseId: string
  ): ViewModel {
    const categories = Object.entries(report.categories)
      .map(([name, payload]) => ({
        name,
        score: payload.score,
        nTasks: payload.n_tasks,
        tasks: Object.entries(payload.tasks)
          .map(([taskName, taskPayload]) => ({
            name: taskName,
            score: taskPayload.score,
            nQuestions: taskPayload.n_questions
          }))
          .sort((a, b) => b.score - a.score)
      }))
      .sort((a, b) => b.score - a.score);

    const sampleQuestions = questions.slice(0, 4).map((question) => ({
      id: question.question_id,
      prompt: question.turns?.[0]?.content ?? 'No prompt',
      category: question.category,
      task: question.task,
      answerType: question.answer_type
    }));

    const licenses = Array.from(new Set(questions.map((q) => q.license))).sort();
    const attributions = Array.from(
      new Set(questions.map((q) => q.attribution))
    ).sort();

    const categoryHeaders = categories.map((category) => category.name);
    const leaderboardRows: LeaderboardRow[] = [
      {
        name: 'Seed sample run',
        subtitle: 'examples/predictions.sample.jsonl',
        overall: report.overall,
        categoryScores: Object.fromEntries(
          categories.map((category) => [category.name, category.score])
        )
      }
    ];

    const year = (questions[0]?.release_date ?? releaseId).slice(0, 4);
    const bibtexYear = /^\d{4}$/.test(year) ? year : '2026';
    const bibtex = [
      `@misc{halachabench${bibtexYear},`,
      `  title = {HalachaBench: Objective Halacha QA Benchmark},`,
      `  year = {${bibtexYear}},`,
      `  howpublished = {Seed release ${releaseId}},`,
      `  note = {Deterministic scoring, closed-format tasks}`,
      `}`
    ].join('\n');

    return {
      releaseId,
      releaseDate: questions[0]?.release_date ?? releaseId,
      bibtex,
      overall: report.overall,
      nQuestions: report.n_questions,
      nMissing: report.n_missing,
      categoryCount: Object.keys(report.categories).length,
      taskCount: Object.keys(report.tasks).length,
      categories,
      categoryHeaders,
      leaderboardRows,
      sampleQuestions,
      licenses,
      attributions
    };
  }
}

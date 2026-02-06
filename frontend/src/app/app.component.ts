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
    return this.autocompleteOpen && this.searchQuery.trim().length >= 2;
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
      fullPrompt,
      haystack
    };
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
    if (!this.showAutocomplete) {
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


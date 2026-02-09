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
  selectedReleaseIndex = this.releaseDates.length - 1;

  private readonly releaseIndex$ = new BehaviorSubject<number>(
    this.selectedReleaseIndex
  );
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

  constructor(private readonly http: HttpClient) {}

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
  }

  private parseJsonl(text: string): Question[] {
    return text
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter((line) => line.length > 0)
      .map((line) => JSON.parse(line) as Question);
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

    const samplePool = questions.filter(
      (question) => question.release_date === releaseId
    );
    const sampleQuestions = (samplePool.length > 0 ? samplePool : questions)
      .slice(0, 4)
      .map((question) => ({
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
      `  howpublished = {Release ${releaseId}},`,
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

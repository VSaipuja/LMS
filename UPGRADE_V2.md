# LearnHub LMS – Additive Upgrade (v2)

This upgrade is designed to preserve the original LMS project and existing SQLite data.
It adds features by introducing a new route module, new templates, and new static assets,
with small integration edits to register the routes and expose navigation/actions.

## Added features

1. **Learning insights** (`/learning/insights`): average quiz score, lesson completion,
   recent quiz performance grouped by quiz, and revision suggestions based on actual scores.
2. **Lesson completion tracking**: students can mark an accessible lesson as completed.
   Completion is saved in the existing `lesson_progress` table and is idempotent.
3. **Study planner** (`/learning/study-planner`): create, complete, and remove personal
   study tasks. Tasks are stored in the browser's local storage on that device only.
4. **Navigation shortcuts**: student navigation and dashboard link to the new modules.

## Files added

- `app/routes/learning.py`
- `app/templates/learning/insights.html`
- `app/templates/learning/study_planner.html`
- `app/static/js/study-planner.js`
- `UPGRADE_V2.md`

## Existing files integrated

- `app/__init__.py` registers the new learning blueprint.
- `app/routes/courses.py` adds a protected lesson-completion endpoint and supplies progress state.
- `app/templates/base.html` adds student navigation links.
- `app/templates/courses/lesson.html` adds the completion action.
- `app/templates/dashboard_student.html` adds shortcuts.
- `app/static/css/style.css` receives appended styles only.

No existing model/table is renamed or dropped. The new functionality reuses the existing
`LessonProgress` model, so `db.create_all()` from the current `run.py` will create that table
if it does not already exist. Existing database rows are not intentionally modified.

## Run on Windows

```powershell
cd lms_project
py -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
py run.py
```

Open `http://127.0.0.1:5000`.

## Important notes

- Existing seeded demo credentials are for local development only. Change/remove them before
  any public deployment.
- The study planner currently uses browser local storage; it is not synchronised across devices.
- Quiz performance is grouped by quiz because the current schema does not tag individual
  questions with topics. Do not describe this as true topic-level weakness detection until
  question-topic mapping and topic mastery are implemented.
- The lesson completion action records the student's self-reported completion. It does not
  verify YouTube watch time.

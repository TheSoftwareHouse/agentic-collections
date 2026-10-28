# Edge cases

Two situations the first run in an empty folder never meets. Both change what the user
is asked, never the shape of the two fixed calls.

## Inside a code repository

`can_be_catalog` is false: the current directory is a git
repository, and `Create <slug>/ here` would nest the project inside one of its own
repositories. Replace the two `Layout` options with these, saying why in the question:

- `Parent folder is the catalog` — `<parent_name>/` becomes the catalog; the context
  repository lands beside this repository. First, and only when `parent_is_git_repo` is
  false and `parent_writable` is true. Its description must warn: right when the parent
  holds only this project's repositories, wrong for a general `projects/` folder, whose
  every session would load the catalog `CLAUDE.md`.
- `Create <slug>/ next to this repository` — a new catalog in `<parent_name>/`; this
  repository stays put, and the skill never moves it, so **Pending decisions** gains a
  fourth item: move `<folder_name>/` into `<slug>/`, then re-run Step 5. Only when
  `parent_writable` is true.
- `Stop` — always, and alone when neither parent option qualifies.

## Overlap warnings

**A `!` overlap warning in the dry run is a question for the user, not a note.** It means
a custom layer names, or is a synonym of, a workspace every project already gets. Quote
it, say which existing workspace covers the topic, and ask whether to drop the layer or
keep it with a distinct scope — before the `Scaffold` call of Step 2, in prose. Two folders
on one topic split the knowledge, and the routing skill then has two plausible
destinations for the same document.

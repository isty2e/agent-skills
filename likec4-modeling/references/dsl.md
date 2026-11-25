# LikeC4 DSL Reference

LikeC4 merges top-level blocks across project `.c4`/`.likec4` files: `specification` defines kinds, `model` declares
elements and relationships, `views` shows structure or interactions, and `deployment` describes where elements run.

## Three-File Example

`architecture/specification.c4`:

```likec4
specification {
  element system
  element worker
  element stateStore
}
```

`architecture/model/jobs.c4`:

```likec4
model {
  jobs = system 'Job Service' {
    recovery = worker 'Recovery Worker'
    store = stateStore 'Job Store' {
      description 'Owns job state and commits transitions.'
    }

    recovery -> store 'Requests job recovery'
  }
}
```

`architecture/views/jobs.c4`:

```likec4
views {
  view jobs-overview of jobs {
    include *
  }

  dynamic view recovery-after-cancel {
    variant sequence
    jobs.recovery -> jobs.store 'Request recovery'
    jobs.recovery <- jobs.store 'Reject: job is cancelled'
  }
}
```

Use qualified nested IDs such as `jobs.store` across files. Sequence participants must have no children. Dynamic steps
can show interactions without corresponding static relationships; declare a model relationship when recording a standing
dependency.

Official syntax: [specification](https://likec4.dev/dsl/specification/), [model](https://likec4.dev/dsl/model/),
[view predicates](https://likec4.dev/dsl/views/predicates/), [dynamic views](https://likec4.dev/dsl/views/dynamic/), and
[model diffs](https://likec4.dev/dsl/diff/). Adapted from the
[official DSL skill](https://github.com/likec4/likec4/tree/2339a2bdf00ab0054ad3c9ac22cc4d09236cd21b/skills/likec4-dsl).

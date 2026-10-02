# Laravel Ecosystem Guidance

## Framework-native first

Laravel has strong, useful conventions. Preserve canonical framework structure and lifecycle unless there is concrete evidence that a particular internal organization is harming the project.

Common framework-owned/canonical areas include:

```text
app/
bootstrap/
config/
database/
public/
resources/
routes/
storage/
tests/
```

Do not relocate these merely to obtain physical feature locality.

## Logical locality

A feature may legitimately span canonical Laravel directories. Make ownership obvious through consistent naming and namespaces:

```text
Orders
  routes       -> routes/...
  HTTP         -> app/Http/...
  domain/app   -> app/Domain/Orders or app/Features/Orders when useful
  model        -> app/Models/Order.php
  views        -> resources/views/orders/
  tests        -> tests/Feature/Orders/
```

Logical locality is agent-friendly when the map is explicit and naming is predictable.

## Flexible areas

Laravel permits substantial organization freedom inside `app/`. For larger domains, `app/Domain/<Domain>` or `app/Features/<Feature>` can improve ownership, but use them only when current complexity warrants them.

## Native extension points

Prefer Laravel service providers, container bindings, events/listeners, jobs/queues, middleware, policies, form requests, commands, resources, and packages before inventing parallel mechanisms.

## Packages

A package boundary is appropriate when functionality truly needs independent distribution/reuse or strong isolation. Do not convert every feature into a package.

## Agent-first verification

Document the project's actual Composer, Artisan, test, lint, static-analysis, and frontend commands. Preserve generators/conventions so agents can leverage framework knowledge.

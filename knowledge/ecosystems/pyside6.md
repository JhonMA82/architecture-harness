# PySide6 / Qt Ecosystem Guidance

## Preserve Qt's model

Use Qt-native concepts: QObject ownership, signals/slots, QMainWindow composition, Model/View for tables/lists/trees, actions, resources, and event lifecycle. Do not wrap Qt in a generic web-style architecture without a demonstrated reason.

## Recommended agent-first direction for substantial desktop apps

A common useful shape is:

```text
core/ or domain/       framework-light domain/shared primitives
features/              product capabilities when locality helps
ui/                    application composition, shared widgets, main window
tools/                  interaction tools when the product naturally has them
formats/                import/export when cross-feature
plugins/                only if a real extension model exists
```

This can be a modular monolith with selective feature slices. Do not force all geometry, viewport primitives, or universal Qt infrastructure into feature folders.

## MainWindow

Treat `QMainWindow` primarily as composition/coordination. Menus, toolbars, trays/docks, and status bar may be extracted into focused composition modules when the window becomes a God Object. Product workflows such as import pipelines or domain operations should not live in MainWindow merely because actions originate there.

## Qt Designer

`.ui` files are appropriate for form-heavy panels/dialogs. Keep generated Python clearly separated from behavioral code. Do not require Designer for complex custom rendering/viewport code that is easier to express programmatically.

Possible organization:

```text
feature/
  panel.py
  form.ui
  generated/ui_form.py
  service.py
  tests/
```

Generated files are not hand-edited.

## Signals/slots

Use signals/slots for UI interaction and decoupling where natural, but do not turn every internal call into an event. Direct calls are clearer when ownership is direct and synchronous.

## Testing

Separate domain/service tests from Qt/widget integration tests. Add startup/smoke tests around application composition when architectural refactors move MainWindow/bootstrap responsibilities.

## Packaging

Packaging (PyInstaller, Briefcase, etc.) is an independent concern. Do not combine a packaging migration with a structural UI/domain refactor unless the contract requires both.

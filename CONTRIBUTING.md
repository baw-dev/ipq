# Contributing

**Answers:** how to change ipq and check the change before proposing it.

- **Change `skill/`, then install it;** never edit an installed copy.
- **The templates in `skill/templates/` are the specification.** The tool
  reads its rules from them, so a rule changes in one place.
- **Run the tests** with `python3 -m unittest discover tests`. They hold
  `tests/fixtures/acme/` and `examples/jinkieslist/` to conformance, and
  check that every chart the README and VISUALS.md quote matches the
  example's generated output. Run `ipq.py fix` on both sets when a block's
  layout changes.
- **Anything under `skill/` needs a version bump** and a CHANGES entry,
  following the policy in [CHANGES.md](CHANGES.md).
- **Try scratch sets** in `demo/` or elsewhere under `examples/`; git ignores
  both, except `examples/jinkieslist/`.

Report problems and ideas as [issues](https://github.com/baw-dev/ipq/issues).

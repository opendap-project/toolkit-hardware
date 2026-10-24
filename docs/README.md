# Documentation

| Folder | Contents |
|---|---|
| [`requirements/`](requirements/) | What this project must achieve. Each requirement has an ID, a priority (**must** / **should**) and a status. |
| [`specs/`](specs/) | Specifications and methods every OpenDAP device shares: the [component export contract](specs/component-export.md), [simulation checks](specs/simulation-checks.md), the [design review checklist](specs/design-review-checklist.md), the [electronics integration and verification method](specs/integration-and-verification.md) and the [PCB design constraints method](specs/pcb-design-constraints-method.md). Each device applies them in its own repositories, the T1 first. |
| [`plans/`](plans/) | Work plans with their task lists: the [hardware engineering system plan](plans/2026-10-hardware-engineering-system-plan.md), which device plans such as the [T1 electronics plan](https://github.com/opendap-project/t1/blob/main/docs/plans/2026-10-electronics-plan.md) apply. |
| [`research/`](research/) | Desk research that informs requirements and decisions. Not a decision by itself. Includes the [compliance regime catalog](research/2026-10-compliance-regimes.md). |

Architecture Decision Records go in `adr/` once decisions are taken.

Only information confirmed by the maintainers is recorded here. Earlier experiments are not a source.

**Requirement status:** *Confirmed* (agreed, build on it) · *Draft* (agreed intent, wording or detail still open).

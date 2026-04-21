# Facts Database Schema

The facts database is a versioned JSON file containing verified ground-truth entries that the hallucination detector checks against.

## Structure

```json
{
  "facts": {
    "fact key (lowercase)": {
      "type": "numeric | string",
      "value": "verified value",
      "unit": "optional unit",
      "tolerance": 0.0,
      "source": "optional source URL or name",
      "verified_date": "2026-04-01"
    }
  }
}
```

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"numeric"` \| `"string"` | ✅ | How the value is compared |
| `value` | string | ✅ | The verified ground-truth value |
| `unit` | string | — | Unit of measure (for display and matching) |
| `tolerance` | float | — | Acceptable numeric deviation (default: 0.0) |
| `source` | string | — | Where this fact was verified |
| `verified_date` | string | — | ISO date when the fact was last verified |

## Examples

### Numeric Fact

```json
{
  "speed of light": {
    "type": "numeric",
    "value": "299792458",
    "unit": "m/s"
  }
}
```

### String Fact

```json
{
  "capital of france": {
    "type": "string",
    "value": "paris"
  }
}
```

### Pricing Fact (with tolerance)

```json
{
  "product monthly price": {
    "type": "numeric",
    "value": "49.99",
    "unit": "usd",
    "tolerance": 0.01
  }
}
```

## Coder Facts Pack

The included `coder_facts_pack_v1.0.json` contains 303 verified coding facts covering:

- Python, JavaScript/TypeScript
- Docker, Git, SQL
- HTTP, Cloud services
- Security, DevOps

Each fact follows the same schema with `source` and `verified_date` fields populated.

## Best Practices

1. **Keep keys lowercase** — matching is case-insensitive
2. **Be specific** — "python 3.12 release date" is better than "python release"
3. **Add units** — helps the detector distinguish "100 USD" from "100 EUR"
4. **Set tolerance** for prices and measurements that may fluctuate
5. **Version your facts file** — treat it like code, commit to git
6. **Verify regularly** — set `verified_date` and review quarterly

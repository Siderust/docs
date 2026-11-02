# Executable examples for the article

Run the commands below from the article directory, with the pinned Rust 1.93.1
toolchain and `examples/Cargo.lock`. The manuscript includes the demonstration
sources directly with `lstinputlisting`.

| Example | Scientific interface illustrated |
| --- | --- |
| `qtty` | A velocity computed and compared as a typed quantity |
| `tempoch` | Explicit UTC-to-TT and JD/MJD conversions, with native formatting |
| `frame_repair` | An explicit frame transformation before position subtraction |
| `surface_contract` | A local body model built from reusable geometry, time and quantity interfaces |
| `runtime_ephemeris` | An explicitly supplied BSP kernel and typed TT epoch |
| `earth_from_moon` | A finite selenocentric target and a generic lunar surface observer |
| `observe` | Historical UT1 Antares pointing with typed site coordinates and angles |

```sh
cargo +1.93.1 run --locked --manifest-path examples/Cargo.toml --bin qtty
cargo +1.93.1 run --locked --manifest-path examples/Cargo.toml --bin frame_repair
cargo +1.93.1 run --locked --manifest-path examples/Cargo.toml --bin surface_contract
cargo +1.93.1 run --locked --manifest-path examples/Cargo.toml --bin observe -- 1896-07-14T20:40:00 2.15017 41.35403
cargo +1.93.1 run --locked --manifest-path examples/Cargo.toml --bin runtime_ephemeris -- /path/to/de440s.bsp
cargo +1.93.1 run --locked --manifest-path examples/Cargo.toml --bin earth_from_moon -- /path/to/de440s.bsp
```

## Representations and scientific boundaries

`antares.rs` keeps angles as `Degrees`, durations as `Seconds` and epochs as
`Time<UT1>`/`Time<TT>`. The grid and planning adapter consume the same
`Geodetic<ECEF>` observer and altitude model. Historical TT is derived from the
prescribed Delta T model. The public BPN operation avoids the generic frame
adapter's redundant historical UTC lookup; the unit-vector invariant at that
rotation boundary is documented. The infallible planning-provider trait is
used within the verified model-coverage window; fallible entry points propagate
conversion errors.

`lunar_application.rs` keeps inertial and body-fixed positions, a typed
displacement, and `HorizontalObservation<Moon, Kilometer>` through the geometry
calculation. The shared site definition is used by the demonstration and
validation programs. Native unit conversion supplies the observer position in
kilometres, and `Position::direction()` checks the center-based direction.
SPK scalar states are interpreted only after checking metadata and coverage,
with physical ICRF realization established from DE440s provenance.

Human-readable output formats quantities directly, preserving units. Raw
scalars are extracted at the low-level SPK interface and at numerical CSV
export boundaries. Rotation matrices and unit-direction components are
naturally dimensionless.

`viewing`, `viewing_events`, `antares_diagnostics`, `historical_feasibility` and
`lunar_geometry` export the existing independent-reference records. They retain
the original CSV schemas and numerical precision. Site coordinates, epochs,
models, search tolerance and recorded results are unchanged.

See [the experiment instructions](../experiments/README.md) for the independent
ERFA/CSPICE checks, hash-pinned kernels and replay commands. Fresh replay
outputs are separate from the preserved `recorded/` evidence.

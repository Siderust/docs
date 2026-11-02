# SPDX-License-Identifier: MIT
"""Shared, dependency-free LaTeX formatting for measured results."""

def scientific(value, decimals=3):
    """Preserve the original tables' four significant figures (zero is unresolved)."""
    if value == 0:
        return '$0$'
    mantissa, exponent = f'{value:.{decimals}e}'.split('e')
    return '$'+mantissa+r'\times10^{'+str(int(exponent))+'}$'


def unit(value):
    if value == '1':
        return '$1$'
    # Text mode keeps the spelled-out angular unit distinct from the degree symbol.
    return r'$\text{deg}$' if value == 'deg' else r'$\mathrm{'+value+'}$'


def statistics_row(name, physical_unit, count, values):
    return (f'{name} & {unit(physical_unit)} & {count} & '+
            ' & '.join(scientific(values[k]) for k in ['median','p95','p99','max'])+r' \\')

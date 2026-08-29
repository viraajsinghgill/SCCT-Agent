from typing import Dict, Any, List

class TariffAndSourcingOptimizer:
    """
    Simulates sourcing allocations across Tier 1 factories (Vietnam, Sri Lanka, Mexico, India)
    under shifting Section 301 tariffs, USMCA duty-free nearshoring, and lead-time constraints.
    Helps Victoria's Secret & Co. balance cost, risk, speed, and ESG quality.
    """
    FACTORY_PROFILES = {
        'Vietnam': {
            'factory_name': 'Crystal International Vietnam Ltd',
            'base_fob_usd': 12.80,
            'standard_duty_pct': 12.0,
            'freight_usd': 0.85,
            'lead_time_days': 38,
            'capacity_monthly': 750000,
            'labor_audit_score': 92,
            'country': 'Vietnam'
        },
        'Sri Lanka': {
            'factory_name': 'MAS Holdings Active Fab',
            'base_fob_usd': 13.20,
            'standard_duty_pct': 8.0,
            'freight_usd': 0.95,
            'lead_time_days': 45,
            'capacity_monthly': 500000,
            'labor_audit_score': 96,
            'country': 'Sri Lanka'
        },
        'Mexico': {
            'factory_name': 'Tegra Global Nearshore Plant',
            'base_fob_usd': 14.90,
            'standard_duty_pct': 0.0, # USMCA duty free
            'freight_usd': 0.40,
            'lead_time_days': 14,
            'capacity_monthly': 300000,
            'labor_audit_score': 89,
            'country': 'Mexico'
        },
        'India': {
            'factory_name': 'Brandix Apparel Eco-Campus',
            'base_fob_usd': 12.50,
            'standard_duty_pct': 10.0,
            'freight_usd': 1.10,
            'lead_time_days': 50,
            'capacity_monthly': 400000,
            'labor_audit_score': 94,
            'country': 'India'
        }
    }

    def simulate_tariff_impact(self, tariff_adjustments: Dict[str, float] = None, total_demand_units: int = 100000) -> Dict[str, Any]:
        """
        Calculates all-in landed cost across factories under modified Section 301 / duty rates.
        tariff_adjustments: e.g. {'Vietnam': 25.0, 'Sri Lanka': 8.0, 'Mexico': 0.0}
        """
        if tariff_adjustments is None:
            tariff_adjustments = {'Vietnam': 12.0, 'Sri Lanka': 8.0, 'Mexico': 0.0, 'India': 10.0}

        results = []
        drayage_handling = 1.25

        for country, profile in self.FACTORY_PROFILES.items():
            duty_rate = tariff_adjustments.get(country, profile['standard_duty_pct'])
            fob = profile['base_fob_usd']
            freight = profile['freight_usd']
            tariff_amount = round(fob * (duty_rate / 100.0), 2)
            total_landed = round(fob + freight + tariff_amount + drayage_handling, 2)
            total_cost_for_order = round(total_landed * total_demand_units, 2)

            results.append({
                'country': country,
                'factory_name': profile['factory_name'],
                'base_fob_usd': fob,
                'tariff_rate_pct': duty_rate,
                'tariff_duty_usd': tariff_amount,
                'freight_usd': freight,
                'drayage_usd': drayage_handling,
                'unit_landed_cost_usd': total_landed,
                'lead_time_days': profile['lead_time_days'],
                'labor_audit_score': profile['labor_audit_score'],
                'total_order_cost_usd': total_cost_for_order
            })

        results.sort(key=lambda x: x['unit_landed_cost_usd'])

        # Recommend optimal dual-sourcing allocation
        primary = results[0]
        secondary = next((r for r in results[1:] if r['country'] == 'Mexico'), results[1])

        recommended_split = {
            'primary_supplier': primary['factory_name'],
            'primary_country': primary['country'],
            'primary_allocation_pct': 65,
            'secondary_supplier': secondary['factory_name'],
            'secondary_country': secondary['country'],
            'secondary_allocation_pct': 35,
            'blended_unit_landed_cost_usd': round((0.65 * primary['unit_landed_cost_usd']) + (0.35 * secondary['unit_landed_cost_usd']), 2),
            'blended_lead_time_days': round((0.65 * primary['lead_time_days']) + (0.35 * secondary['lead_time_days']), 1),
            'rationale': f"Balancing lowest landed cost ({primary['country']} @ ${primary['unit_landed_cost_usd']}/unit) with nearshore speed and zero-tariff agility ({secondary['country']} @ {secondary['lead_time_days']} days lead time)."
        }

        return {
            'total_demand_units': total_demand_units,
            'factory_comparisons': results,
            'recommended_split': recommended_split
        }

tariff_optimizer = TariffAndSourcingOptimizer()

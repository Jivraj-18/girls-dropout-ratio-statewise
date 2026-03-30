# UDISE girls dropout — quick findings (derived from cohort-flow tables)

Data: UDISE archive `mapId=117`, years 16–22, caste_id=5 (Overall).

## National picture (latest year)

- Primary girls dropout: 1.32%
- Upper primary girls dropout: 3.21%
- Secondary girls dropout: 12.46%

## Status-quo forecast (national, secondary girls)

Linear trend over available years implies ~-1.40 pp/year change.
Next 3-year projection (percentage): 11.98%, 10.58%, 9.17%

## State ranking (secondary girls dropout, latest year)

| State/UT          |   Year |   Secondary girls dropout (%) |
|:------------------|-------:|------------------------------:|
| Odisha            |     21 |                       25.2846 |
| Meghalaya         |     21 |                       21.9741 |
| Bihar             |     21 |                       21.447  |
| Assam             |     21 |                       21.2257 |
| West Bengal       |     21 |                       18.4686 |
| Nagaland          |     21 |                       17.7145 |
| Punjab            |     21 |                       16.0711 |
| Gujarat           |     21 |                       15.8903 |
| Andhra Pradesh    |     21 |                       14.9572 |
| Karnataka         |     21 |                       13.2871 |
| Arunachal Pradesh |     21 |                       12.9935 |
| Telangana         |     21 |                       12.9441 |
| Mizoram           |     21 |                       11.3213 |
| Sikkim            |     21 |                       10.8871 |
| Maharashtra       |     21 |                       10.7263 |


## Biggest improvements vs. deteriorations (secondary girls, first→latest)

### Most improved (dropout fell)

| State/UT        |   Change (pp) |
|:----------------|--------------:|
| Tripura         |        -33.25 |
| Madhya Pradesh  |        -23.23 |
| Chhattisgarh    |        -16.67 |
| Jharkhand       |        -16.03 |
| Manipur         |        -14.37 |
| Assam           |        -11.99 |
| Jammu & Kashmir |        -11.82 |
| Mizoram         |        -11.74 |
| Haryana         |        -11.21 |
| Karnataka       |        -11.12 |


### Most worsened (dropout rose)

| State/UT                  |   Change (pp) |
|:--------------------------|--------------:|
| Punjab                    |          6.99 |
| Chandigarh                |          0    |
| Uttar Pradesh             |         -0.65 |
| Andhra Pradesh            |         -0.65 |
| Telangana                 |         -1.56 |
| Maharashtra               |         -2.16 |
| Tamilnadu                 |         -2.22 |
| Arunachal Pradesh         |         -2.8  |
| Andaman & Nicobar Islands |         -3    |
| Meghalaya                 |         -3.02 |


## Notes on method

Rates are derived from the tabular cohort-flow counts (previous cohort, next-grade current, fresh admissions, repeaters):
- Promoted ≈ (next_grade_current_total − next_grade_fresh)
- Repeat = same_grade_repeaters
- Dropout = previous − promoted − repeat (clipped at 0)

# SupplierTrust Week 02 — Claim verification

| Film claim | Evidence and exact scope | On-screen attribution | Guardrail |
|---|---|---|---|
| NIST frames due diligence as research into pertinent supplier information before decisions. | NIST SP 1326, Abstract; final 8 July 2026. | NIST · SP 1326 · 2026 | The guide is cybersecurity supply-chain guidance scoped to ICT suppliers. It does not certify SupplierTrust. |
| Fewer than one in five large listed companies report evaluating supplier risk against environmental or human-rights criteria. | OECD Responsible Business Outlook 2026, Figure 2.6; 16% environmental, 18% human-rights. | OECD · Responsible Business Outlook 2026 · Fig. 2.6 | Public disclosures from large listed companies; these measures are partial proxies, not a complete assessment of due diligence and not representative of every company. |
| Many potential OFAC screening matches are false positives and should be compared against full available details. | U.S. Treasury OFAC, “Assessing OFAC Name Matches,” FAQ 5, Step 3. | U.S. Treasury · OFAC FAQ 5 | The demo record is synthetic, not a real sanctions hit; a name alert alone is not a conclusion. |
| SupplierTrust displays a deterministic concern index, recorded evidence, synthetic screening, review history and a text report. | Observed in the deployed fictional demo on 20 November 2026; captured from the production website by Playwright. | SupplierTrust · fictional read-only demo | Describes current implemented demo behavior only; does not claim fraud prediction or independently verified evidence authenticity. |
| React presents the workflow; FastAPI serves the API; PostgreSQL is supported by the writable local application; the public demo uses a fixed fictional fixture. | Repository architecture and deployment configuration inspected for this production; hosted demo behavior verified during Stage 1. | SupplierTrust · implementation notes | The public demo is read-only and does not store visitor assessments. Do not imply hosted database persistence for demo records. |

## Source links

- NIST SP 1326: https://csrc.nist.gov/pubs/sp/1326/final
- OECD chapter 2: https://www.oecd.org/en/publications/oecd-responsible-business-outlook-2026_2b15370f-en/full-report/how-are-companies-implementing-due-diligence-for-responsible-business-conduct_52523408.html
- OFAC FAQ 5: https://ofac.treasury.gov/faqs/topic/1591

# 🧪 Selected RAG Test Questions (Top 60)

This document contains **60 high-impact questions** designed to test the RAG system's understanding of the User Corpus (Pismo/Real-Time Core Accounts). They are structured by domain complexity.

---

## 🏗️ Phase 1: Foundational Structure & Setup
*These questions validate that the RAG understands the core building blocks of the platform.*

### 1. General Platform Knowledge
1.  What is the primary purpose of the “Real-Time Core Accounts OPS” platform?
2.  Which specific modules are available under the "Platform Setup" menu?
3.  What is the difference between specific record statuses: “Active”, “In Pipeline”, and “Processed”?

### 2. Program & Account Architecture
4.  What is a “Program” in the Pismo context and how does it relate to Accounts?
5.  Why do we need different Programs for different time zones?
6.  What is an **Account Class** and how does it link DDA accounts to the General Ledger?
7.  What does `Account Class Type = "U"` indicate?
8.  How do I identify which CURRENT-ACCOUNTS programs are currently active?

### 3. Branch & Holiday Governance
9.  How is a **Branch Code** used in transaction processing?
10. What is the mandatory relationship between Branch, Holiday Center, and Country Code?
11. How do configured Holidays affect transaction settlement dates?
12. What is the functional difference between a “Bank Holiday” and a “Bank *Local* Holiday”?

---

## 💳 Phase 2: Transaction & Payment Logic (Core Domain)
*These questions test deep domain knowledge essential for payments professionals.*

### 4. Transaction Code Logic
13. What is a **Transaction Code** and how does it differ from a Processing Code?
14. How does a Transaction Code map to SWIFT standards?
15. What does the “Available Days” parameter control?
16. What does `Sanction Flag = Y` imply for a transaction?

### 5. Processing Codes (The "Engine")
17. What specifically is a **Processing Code** in Pismo?
18. Explain the difference between `Balance Impact = 1` and `Balance Impact = -1`.
19. What distinguishes a "Reversal" code from a "Partial Reversal" code?
20. Why would a Processing Code show a status of “SUCCESS” but not affect the balance?
21. How can a user verify if a Processing Code has been successfully deployed?

---

## 🛡️ Phase 3: Risk, Compliance & Authorization
*Questions focusing on security, approvals, and error handling.*

### 6. Maker-Checker & Approvals
22. Which specific modules require a **Maker-Checker** (authorization) flow?
23. What specific actions can a "Maker" perform versus a "Checker"?
24. What does the status `Auth Required` mean for a new record (e.g., Branch or Transaction Code)?
25. Who has the permission to approve compliance-rejected records?

### 7. Dormancy & Sanctions
26. What logic does **Dormancy Configuration** control?
27. What does `Target Type = Division` mean in dormancy rules?
28. If `Deny = True` is set for a dormant account, what happens to incoming transactions?
29. How are sanction checks enforced across different modules?

---

## 🔧 Phase 4: Critical Operations (High Risk)
*These are the most important questions for operational support teams.*

### 8. Manual Adjustments (UETR & Repairs)
30. When is a **Manual Adjustment** strictly required?
31. What is the **UETR** (Unique End-to-End Transaction Reference) and why is it critical?
32. What actions can an operator perform when a record is in “In Process” status?
33. What does the status **Pending Repair** indicate?
34. Why would a Manual Adjustment be rejected for “Sanctions” reasons?
35. Can a rejected adjustment be resubmitted, or must it be recreated?
36. How does the system ensure an audit trail for all manual adjustments?

### 9. Account Inquiry & Troubleshooting
37. What specific data points can be retrieved via the **Account Inquiry** screen?
38. What is the maximum date range allowed for a single inquiry?
39. Which module should be the first step in troubleshooting a failed transaction?

---

## 🧠 Phase 5: Advanced Reasoning (The "RAG" Test)
*These questions require the AI to synthesize information from multiple sections/pages. They are the best test of "intelligence".*

40. Why can a **Transaction Code** be active while its linked **Branches** are still in the pipeline?
41. Exactly what reference data must be active *before* any transactions can be processed?
42. What are the specific dependencies between a Branch, a Holiday, and a Transaction Code?
43. What specific conditions could prevent a manual adjustment from posting successfully?
44. Why do multiple Programs exist for the same Currency and Country combination?
45. How does the "Check Time" parameter in Dormancy interact with transaction timestamps?

---

## ❓ Phase 6: Operational "FAQs"
*Common questions users ask when things look "wrong".*

46. Why do many "Active" tabs show “No records found” initially?
47. Is it expected behavior for a production environment to start with empty reference data?
48. How can I validate whether data is actually missing or simply filtered out by the UI?
49. Why is a specific Branch record showing in an **Error** state?
50. What does `Account Class Type` differences imply for reporting?

---

## 📋 Phase 7: Setup & Modification Procedures
*“How-To” questions for setting up the system.*

51. What is the step-by-step process to move an Account Class from "Pipeline" to "Active"?
52. How do I create a new Processing Code, and what approvals will be triggered?
53. What is the recommended sequence for creating reference data (which comes first)?
54. How do I activate a Dormancy Configuration that is currently INACTIVE?
55. Who is authorized to resolve errors in the Branch pipeline?
56. Where do I start if I need to onboard a new Country?
57. How do I search for holidays specifically by division?
58. How do I identify the Unique Reference ID for an RTCA transaction?
59. How do I check records that are "In Pipeline"?
60. What is the difference between Account Class Code and Reference ID?

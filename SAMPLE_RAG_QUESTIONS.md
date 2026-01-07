# Sample RAG Questions (User Corpus)

This document serves as a test suite for the RAG system. These questions are designed to validate the system's ability to retrieve specific operational knowledge from the User Corpus (Real-Time Core Accounts OPS / Pismo platform).

## 1. General / Navigation Questions (Foundational RAG)
*These validate whether the RAG can understand structure, breadcrumbs, and purpose.*

1.  What is the purpose of the “Real-Time Core Accounts OPS” platform?
2.  Which modules are available under Platform Setup?
3.  What is the difference between “Active”, “In Pipeline”, and “Processed” records across modules?
4.  Which modules support maker–checker (authorization) flow?
5.  What actions can a user perform from the Services Reference Data Hub?

---

## 2. Processing Code Setup (High-Value Domain Checks)
*Conceptual*
6.  What is a Processing Code and how does it affect transactions in Pismo?
7.  What does “Balance Impact = 1 vs -1” mean in Processing Codes?
8.  What is a Reversal Processing Code vs Partial Reversal Processing Code?

*Operational*
9.  How do I check if a Processing Code is active and successfully deployed?
10. Why does a Processing Code show status as “SUCCESS” at Pismo?
11. Why are there no records in “Processing Codes in Pipeline”?
12. How do I create a new Processing Code and what approvals are required?

---

## 3. Transaction Code Module (Payments Criticality)
*Conceptual*
13. What is a Transaction Code and how is it different from a Processing Code?
14. How does a Transaction Code link to SWIFT and product alignment?
15. What does “Available Days” indicate in a Transaction Code?

*Authorization & Compliance*
16. What does “Auth Required” status mean in Transaction Codes?
17. What does “Sanction Flag = Y” imply?
18. Why would a Transaction Code fail authorization?
19. Who can authorize Transaction Codes in pipeline?

---

## 4. Account Class (Core Banking Knowledge)
*Conceptual*
20. What is an Account Class and why is it needed?
21. How does Account Class link DDAs to General Ledger accounts?
22. What is the difference between Account Class Code and Reference ID?

*Operational*
23. Why are no records visible in Active Account Classes?
24. How do I move an Account Class from Pipeline to Active?
25. What does Account Class Type = “U” indicate?

---

## 5. Branch Management (Reference Data Governance)
*Conceptual*
26. What is a Branch Code used for in transactions?
27. How does Branch relate to Holiday Center Code and Country Code?

*Operational*
28. Why are there no Active Branch Codes?
29. What does “Auth Required” mean for Branch creation?
30. Why is a Branch record in Error state?
31. Who can resolve Branch pipeline errors?

---

## 6. Holiday Setup (Time & Settlement Logic)
*Conceptual*
32. What is Holiday Setup used for in Pismo?
33. How do holidays affect transaction processing?
34. What is the relationship between Holiday, Division, and Country?

*Data-driven*
35. How many holidays are configured for the US division?
36. What is the difference between “Holiday”, “Bank Holiday”, and “Bank Local Holiday”?
37. How can I search for holidays by date or division?

---

## 7. Dormancy Configuration (Risk & Compliance)
*Conceptual*
38. What does Dormancy Configuration control?
39. What does “Target Type = Division” mean?
40. What does “Check Time” represent?

*Operational*
41. Why are all Dormancy Configurations marked INACTIVE?
42. What does “Deny = True” imply for dormant accounts?
43. How do I activate or modify a Dormancy Configuration?

---

## 8. Manual Adjustments (High-Risk Operations)
*Conceptual*
44. What is a Manual Adjustment and when is it required?
45. What is UETR and why is it important?
46. What is RTCA Unique Reference ID?

*Workflow*
47. What happens during Pending Authorization/Reauthorization?
48. What does Pending Repair mean?
49. What actions are allowed in “In Process” status?
50. Why would a Manual Adjustment be rejected for compliance reasons?

*Troubleshooting*
51. Why is a manual adjustment showing status “Error”?
52. What does “Rejected Sanctions” mean?
53. Can a rejected manual adjustment be resubmitted?

---

## 9. Account Inquiry (Read-Only Intelligence)
54. What information can be retrieved from Account Inquiry?
55. What is the maximum allowed date range for account inquiry?
56. Why is account number mandatory?

---

## 10. Program Setup (Product Architecture)
*Conceptual*
57. What is a Program in Pismo?
58. How does Program relate to Accounts and Currency?
59. Why do programs have different time zones?

*Operational*
60. How do I identify the active CURRENT-ACCOUNTS programs?
61. Why do multiple programs exist for the same currency and country?

---

## 11. Advanced RAG / Cross-Module Questions (Reasoning Test)
*These test true RAG intelligence beyond keyword matching.*

62. Why can a Transaction Code be active while Branches are still in pipeline?
63. What reference data must be active before transactions can be processed?
64. What are the dependencies between Branch, Holiday, and Transaction Code?
65. Which modules require authorization before becoming active?
66. What could prevent a manual adjustment from posting successfully?

---

## 12. Role-Based Questions (Enterprise Chat)
67. What actions can a Maker perform vs a Checker?
68. Which modules are read-only for non-admin users?
69. Who can approve compliance-rejected records?

---

## 13. Audit & Compliance
70. How does the system ensure audit trail for manual adjustments?
71. Where can I see who last acted on a record?
72. How are sanction checks enforced across modules?

---

## 14. "Why is this empty?" (Operational Debugging)
73. Why do many Active tabs show “No records found”?
74. Is it expected that production environments start with empty reference data?
75. How can I validate whether data is missing or simply filtered?

---

## 15. Meta / Chat UX
76. Which module should I use to troubleshoot a failed transaction?
77. Where do I start if I’m onboarding a new country or branch?
78. What sequence should reference data be created in?

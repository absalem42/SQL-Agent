# 📊 Metrics Definitions

This document contains definitions for key business and system metrics, their calculation logic, and related metadata.  
It is the single source of truth for analytics across Finance, Sales, Inventory, and Digital Operations (ERP).

---

## 🧮 Finance Metrics

### **Accounts Receivable (AR)**
- **Definition:** Total outstanding customer invoices or money owed to the company for goods or services delivered but not yet paid for.
- **Formula:**  
  \[
  \text{AR Balance} = \text{Sum of (Outstanding Invoices)}
  \]
- **Module:** `finance`
- **Tags:** `liquidity,working-capital`
- **Created At:** 2025-09-11

---

### **Revenue**
- **Definition:** Total income generated from the sale of goods or services before expenses are deducted.
- **Formula:**  
  \[
  \text{Revenue} = \text{Units Sold} \times \text{Selling Price per Unit}
  \]
- **Module:** `finance`
- **Tags:** `KPI,financial,topline`
- **Created At:** 2025-09-11

---

### **Invoice Processing Time**
- **Definition:** Average time taken from invoice generation to payment collection.
- **Formula:**  
  \[
  \text{Invoice Processing Time} = \frac{\text{Sum of (Payment Date - Invoice Date)}}{\text{Number of Invoices Paid}}
  \]
- **Module:** `finance`
- **Tags:** `efficiency,collections`
- **Created At:** 2025-09-11

---

### **Compliance Violation Rate**
- **Definition:** Percentage of financial transactions that failed to meet internal compliance rules or approval workflows.
- **Formula:**  
  \[
  \text{Violation Rate (\%)} = \frac{\text{Non-Compliant Transactions}}{\text{Total Transactions}} \times 100
  \]
- **Module:** `finance`
- **Tags:** `audit,governance`
- **Created At:** 2025-09-11

---

## 📦 Inventory & Operations Metrics

### **Economic Order Quantity (EOQ)**
- **Definition:** The optimal order quantity that minimizes total inventory costs, including ordering costs and holding costs.
- **Formula:**  
  \[
  \text{EOQ} = \sqrt{\frac{2DS}{H}}
  \]
  Where:  
  - \( D \) = Demand (units per year)  
  - \( S \) = Ordering cost per order  
  - \( H \) = Holding cost per unit per year
- **Module:** `inventory`
- **Tags:** `inventory,optimization`
- **Created At:** 2025-09-11

---

### **Stockout Rate**
- **Definition:** Percentage of orders delayed or canceled due to inventory shortages.
- **Formula:**  
  \[
  \text{Stockout Rate (\%)} = \frac{\text{Orders Affected by Stockouts}}{\text{Total Orders}} \times 100
  \]
- **Module:** `inventory`
- **Tags:** `inventory,service-level`
- **Created At:** 2025-09-11

---

### **Order Cycle Time**
- **Definition:** Average time from order creation to order fulfillment.
- **Formula:**  
  \[
  \text{Order Cycle Time} = \frac{\text{Sum of (Fulfillment Date - Order Date)}}{\text{Total Orders}}
  \]
- **Module:** `operations`
- **Tags:** `logistics,efficiency`
- **Created At:** 2025-09-11

---

### **On-Time Delivery Rate**
- **Definition:** Percentage of orders delivered to customers on or before the promised delivery date.
- **Formula:**  
  \[
  \text{On-Time Delivery Rate (\%)} = \frac{\text{On-Time Deliveries}}{\text{Total Deliveries}} \times 100
  \]
- **Module:** `operations`
- **Tags:** `logistics,customer-satisfaction`
- **Created At:** 2025-09-11

---

## 💼 Sales Metrics

### **Lead Score**
- **Definition:** A numerical value that represents the probability a lead will convert into a paying customer.
- **Formula:**  
  \[
  \text{Lead Score} = \text{Weighted Sum of Attributes (Engagement, Fit, Recency)}
  \]
  *(Exact weights depend on business scoring model)*
- **Module:** `sales`
- **Tags:** `lead,conversion,predictive`
- **Created At:** 2025-09-11

---

### **Sales Conversion Rate**
- **Definition:** Percentage of qualified leads that convert into paying customers.
- **Formula:**  
  \[
  \text{Conversion Rate (\%)} = \frac{\text{Closed Deals}}{\text{Qualified Leads}} \times 100
  \]
- **Module:** `sales`
- **Tags:** `sales-performance,KPI`
- **Created At:** 2025-09-11

---

### **Quote-to-Cash Time**
- **Definition:** Average number of days from quote issuance to cash collection.
- **Formula:**  
  \[
  \text{Quote-to-Cash Time} = \frac{\text{Sum of (Payment Date - Quote Date)}}{\text{Number of Deals}}
  \]
- **Module:** `sales`
- **Tags:** `sales-cycle,efficiency`
- **Created At:** 2025-09-11

---

## 🤖 Digital Operations & ERP Metrics

### **Agent Resolution Rate**
- **Definition:** Percentage of employee requests successfully handled by AI agents without human intervention.
- **Formula:**  
  \[
  \text{Agent Resolution Rate (\%)} = \frac{\text{Agent-Resolved Requests}}{\text{Total Requests}} \times 100
  \]
- **Module:** `erp-doi`
- **Tags:** `automation,ai-performance`
- **Created At:** 2025-09-11

---

### **Average Query Response Time**
- **Definition:** Average time taken by the agent-driven ERP system to respond to user queries.
- **Formula:**  
  \[
  \text{Avg. Response Time} = \frac{\text{Sum of Response Times}}{\text{Number of Queries}}
  \]
- **Module:** `erp-doi`
- **Tags:** `latency,user-experience`
- **Created At:** 2025-09-11

---

### **User Adoption Rate**
- **Definition:** Percentage of employees actively using the new ERP system compared to total target users.
- **Formula:**  
  \[
  \text{User Adoption Rate (\%)} = \frac{\text{Active ERP Users}}{\text{Total Target Users}} \times 100
  \]
- **Module:** `erp-doi`
- **Tags:** `adoption,KPI`
- **Created At:** 2025-09-11

---

### **Workflow Automation Coverage**
- **Definition:** Percentage of enterprise workflows automated within the ERP system compared to total identified workflows.
- **Formula:**  
  \[
  \text{Automation Coverage (\%)} = \frac{\text{Automated Workflows}}{\text{Total Workflows Identified}} \times 100
  \]
- **Module:** `erp-doi`
- **Tags:** `process-automation,efficiency`
- **Created At:** 2025-09-11

---

### **Insight Delivery Speed**
- **Definition:** Average time from data update to analytics insight availability for executives.
- **Formula:**  
  \[
  \text{Insight Delivery Speed} = \frac{\text{Sum of (Insight Available Time - Data Update Time)}}{\text{Number of Insights Delivered}}
  \]
- **Module:** `erp-doi`
- **Tags:** `analytics,decision-support`
- **Created At:** 2025-09-11

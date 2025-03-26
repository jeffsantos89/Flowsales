# API Documentation - Marketing Automation Service

## Introdução
Esta API permite gerenciar leads, campanhas e prever churn.

---

## **Endpoints**

### **1. Leads**
- **GET /api/leads**
  - **Descrição:** Retorna todos os leads.
  - **Resposta:**
    ```json
    [
      {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "status": "active"
      }
    ]
    ```

- **POST /api/leads**
  - **Descrição:** Cria um novo lead.
  - **Body:**
    ```json
    {
      "name": "John Doe",
      "email": "john@example.com",
      "source": "Website"
    }
    ```

---

### **2. Campanhas**
- **GET /api/campaigns**
  - **Descrição:** Retorna todas as campanhas.

- **POST /api/campaigns**
  - **Descrição:** Cria uma nova campanha.
  - **Body:**
    ```json
    {
      "name": "Campanha 2025",
      "type": "Email",
      "status": "active"
    }
    ```

---

### **3. Churn Prediction**
- **POST /api/analytics/churn**
  - **Descrição:** Prediz a probabilidade de churn para um lead.
  - **Body:**
    ```json
    {
      "leadId": 1
    }
    ```

---

### **Autenticação**
Todos os endpoints são protegidos por API Key.

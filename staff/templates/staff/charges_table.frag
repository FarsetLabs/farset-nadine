<h3>{{ name }}</h3>
<table>
    <tr class="row-even">
        <th>Member</th>
        <th>Description</th>
        <!--<th>Type</th>-->
        <th>Status</th>
        <th>Charge</th>
        <th>Bill</th>
        <th>Invoice</th>
        <th>Action</th>
    </tr>

    {% for t in transactions %}
        <!-- transaction_id: {{ t.transaction_id }} -->
        <tr>
            <td><a href="{% url 'staff_user_detail' t.username %}">{{ t.username }}</a></td>
            <td>{{ t.description }}</td>
            <!--<td>{{ t.card_type }}</td>-->
            <td {% if t.status == "Authorized" %} style="color:green;"{% endif %}>{{ t.status }}</td>
            <td {% if t.open_bill_amount and t.open_bill_amount != t.amount %} style="color:red;" {% endif %}>
                {{ t.amount|floatformat:2 }}
            </td>
            <td>
                {% if t.open_bill_amount %} ${{ t.open_bill_amount|floatformat:2 }} {% endif %}
            </td>
            <td>
                {% for i in t.xero_invoices %}
                    <a href="https://go.xero.com/AccountsReceivable/View.aspx?InvoiceID={{ i.InvoiceID }}" target="_new">{{ i.InvoiceNumber }}</a><br>
                {% endfor %}
            </td>
            <td style="text-align:center;">
                <a href="{% url 'staff_user_payment' t.username %}"><input type="button" value="U"></a>
                <a href="{% url 'staff_xero' t.username %}"><input type="button" value="X"></a>
                {% ifequal "Authorized" t.status %}
                    <form action="{% url 'staff_payment_void' %}" method="POST" style="display:inline;">
                        <input type="hidden" name="transaction_id" value="{{ t.transaction_id }}" />
                        <input type="submit" value="Void"/>
                        {% csrf_token %}
                    </form>
                {% endifequal %}
                {% if t.open_bill_amount %}
                    <form action="{% url 'staff_bills_paid' t.username %}" method="POST" style="display:inline;">
                        <input type="hidden" name="next" value="{{request.path}}" />
                        <input type="submit" value="Paid"/>
                        {% csrf_token %}
                    </form>
                {% endif %}
            </td>
        </tr>
    {% endfor %}

    <tr class="row-even">
        <td><strong>{{ transactions|length }} Transactions</strong></td>
        <td></td>
        <td style="text-align:right;"><strong>Total</strong></td>
        <td>${{total|floatformat:2}}</td>
        <td colspan="3"></td>
    </tr>
</table>


const form = document.getElementById("orderForm");

const item = document.getElementById("item");
const quantity = document.getElementById("quantity");

const API_URL = "https://3z3aukttf6.execute-api.ap-southeast-2.amazonaws.com/orders";

function updateBill() {
    const selectedOption = item.options[item.selectedIndex];

    const foodName = item.value;
    const price = Number(selectedOption.dataset.price);
    const qty = Number(quantity.value) || 0;

    const total = price * qty;

    document.getElementById("summary").innerText =
        foodName + " × " + qty;

    document.getElementById("total").innerText =
        "Total: ₹" + total;
}

item.addEventListener("change", updateBill);
quantity.addEventListener("input", updateBill);

form.addEventListener("submit", async function(event) {

    event.preventDefault();

    if (!form.reportValidity()) return;

    const message = document.getElementById("message");

    const order = {
        name: document.getElementById("name").value,
        phone: document.getElementById("phone").value,
        email: document.getElementById("email").value,
        address: document.getElementById("address").value,
        city: document.getElementById("city").value,
        pincode: document.getElementById("pincode").value,
        landmark: document.getElementById("landmark").value,
        food: item.value,
        quantity: Number(quantity.value),
        instructions: document.getElementById("instructions").value,
        payment: document.getElementById("payment").value,
        total: Number(item.options[item.selectedIndex].dataset.price)
               * Number(quantity.value)
    };

    message.innerText = "Placing your order... ⏳";

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(order)
        });

        const result = await response.json();

        if (!response.ok || !result.orderId) {
            throw new Error(result.message || "Order failed");
        }

        message.innerText =
            "Order placed successfully! 🎉\n" +
            "Thank you, " + order.name + "!\n" +
            "Order ID: " + result.orderId + "\n" +
            "Your order: " + order.quantity + " " +
            order.food + "(s)\n" +
            "Total: ₹" + order.total + "\n" +
            "Payment: " + order.payment;

    } catch (error) {
        message.innerText =
            "Unable to place order. Please try again.";
        console.error(error);
    }
});

updateBill();

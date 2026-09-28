const modal = document.getElementById("ticketModal");
const form = document.getElementById("ticketForm");
const message = document.getElementById("formMessage");


function openTicketForm() {
    modal.classList.add("active");
}


function closeTicketForm() {
    modal.classList.remove("active");
    form.reset();
    message.classList.remove("show");
    message.textContent = "";
}


modal.addEventListener("click", function (event) {

    if (event.target === modal) {
        closeTicketForm();
    }

});


form.addEventListener("submit", async function (event) {

    event.preventDefault();

    const ticketData = {
        title: document.getElementById("title").value,
        description: document.getElementById("description").value,
        category: document.getElementById("category").value,
        priority: document.getElementById("priority").value,

        // Temporary logged-in employee
        created_by: currentUserId
    };


    try {

        const response = await fetch("/api/tickets", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(ticketData)

        });


        const result = await response.json();


        if (!response.ok) {

            message.textContent =
                result.error || "Failed to create ticket.";

            message.classList.add("show");

            return;
        }


        message.textContent =
            `Ticket #${result.ticket_id} created successfully.`;

        message.classList.add("show");


        form.reset();


        setTimeout(function () {
            window.location.reload();
        }, 800);


    } catch (error) {

        message.textContent =
            "Unable to connect to the server.";

        message.classList.add("show");

        console.error(error);

    }

});


async function confirmTicket(ticketId) {

    const confirmed = confirm(
        "Are you sure the issue has been resolved?"
    );

    if (!confirmed) {
        return;
    }

    try {

        const response = await fetch(
            `/api/tickets/${ticketId}/confirm`,
            {
                method: "PUT",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    user_id: 1
                })
            }
        );


        const result = await response.json();


        if (!response.ok) {

            alert(
                result.error ||
                "Unable to confirm ticket."
            );

            return;
        }


        /*
         * Confirmation succeeded.
         *
         * Now close the ticket.
         */

        const closeResponse = await fetch(
            `/api/tickets/${ticketId}/close`,
            {
                method: "PUT",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    closed_by: 1
                })
            }
        );


        const closeResult = await closeResponse.json();


        if (!closeResponse.ok) {

            alert(
                closeResult.error ||
                "Ticket was confirmed but could not be closed."
            );

            return;
        }


        alert(
            `Ticket #${ticketId} has been closed successfully.`
        );


        window.location.reload();

    } catch (error) {

        console.error(error);

        alert(
            "Unable to connect to the server."
        );
    }
}
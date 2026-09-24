let selectedTicketId = null;


function openAssignModal(ticketId) {

    selectedTicketId = ticketId;

    document.getElementById("assignTicketId").value = ticketId;

    document
        .getElementById("assignModal")
        .classList.add("active");
}


function closeAssignModal() {

    document
        .getElementById("assignModal")
        .classList.remove("active");

    document.getElementById("agentSelect").value = "";

    selectedTicketId = null;
}


async function assignTicket() {

    const agentId =
        document.getElementById("agentSelect").value;


    if (!agentId) {

        alert("Please select an agent.");

        return;
    }


    try {

        const response = await fetch(
            `/api/tickets/${selectedTicketId}/assign`,
            {
                method: "PUT",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    assigned_to: parseInt(agentId)
                })
            }
        );


        const result = await response.json();


        if (!response.ok) {

            alert(result.error || "Assignment failed.");

            return;
        }


        alert("Ticket assigned successfully.");

        window.location.reload();

    }

    catch (error) {

        console.error(error);

        alert("Unable to connect to the server.");

    }
}


async function updateStatus(ticketId, newStatus) {

    try {

        const response = await fetch(
            `/api/tickets/${ticketId}/status`,
            {
                method: "PUT",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    status: newStatus,

                    // Temporary agent
                    changed_by: 2
                })
            }
        );


        const result = await response.json();


        if (!response.ok) {

            alert(result.error || "Status update failed.");

            return;
        }


        alert(
            `Ticket status changed to ${newStatus}.`
        );


        window.location.reload();

    }

    catch (error) {

        console.error(error);

        alert("Unable to connect to the server.");

    }
}
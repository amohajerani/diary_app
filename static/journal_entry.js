function shareViaEmail(entry_id) {
  var email = prompt("Please enter your email address:")
  if (email) {
    var payload = {
      entry_id: entry_id,
      email: email,
    }
    fetch("/email_content", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    })
      .then((response) => {
        if (response.ok) {
          alert("Email sent successfully!")
        } else {
          alert("Failed to send email.")
        }
      })
      .catch((error) => {
        console.error("Error:", error)
        alert("An error occurred while sending the email.")
      })
  }
}

function change_to_in_progress(entry_id) {
  fetch('/change-to-in-progress', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({'entry_id':entry_id})
  })
  .then(response => {
    if (response.ok) {
      // If the POST request is successful, redirect the browser to the second endpoint
      window.location.href = '/chat/'+entry_id;
    } else {
      throw new Error('Failed to send POST request.');
    }
  })
  .catch(error => {
    console.error(error);
  });
}

function downloadAsPDF() {
  window.print()
}
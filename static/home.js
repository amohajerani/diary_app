
  function deleteItem(element, entry_id) {
    var listItem = element.parentNode;
    var confirmation = confirm("Are you sure you want to delete the entry?");
    if (confirmation) {

    // Send a fetch request to remove the item from the database
    fetch('/delete-entry/' + entry_id, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(response => {
      if (response.ok) {
        // On successful deletion, remove the list item from the DOM
        listItem.parentNode.removeChild(listItem);
        window.location.href = '/';
      } else {
        // Handle error case
        console.log('Failed to delete item');
      }
    })
    .catch(error => {
      // Handle network error
      console.log('Network error occurred');
    });
  }
}

function togglePrivacy(element, entryId) {
  const text = element.innerText.trim();
  var confirmation = true;
  if (text=='Private') {
    var confirmation = confirm("This will make the entry visible to others. While the entry will be posted anonymously, the content of the entry may contain personal information. Do you want to proceed?");
    }
  if (confirmation) {
  const updatedText = text === 'Private' ? 'Public' : 'Private';
  element.innerText = updatedText;
  const data = {
    entry_id: entryId,
    private: updatedText === 'Private'
  };

    // Send a POST request to the server-side endpoint for updating the privacy
    fetch('/update-privacy', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    .then(response => {
      // Handle the response as needed
      if (response.ok) {
        console.log('Privacy updated successfully');
      } else {
        console.error('Failed to update privacy');
      }
    })
    .catch(error => {
      console.error('An error occurred while updating privacy', error);
    });

  // Optional: You can also add visual cues or styles to indicate the privacy status change.
  element.classList.toggle('private');
  element.classList.toggle('public');
}
}
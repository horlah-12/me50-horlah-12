document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
    document.querySelector('#compose-form').addEventListener('submit', function(e) {
    e.preventDefault();
    sendEmail();
  });

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
 fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
      console.log('mailbox:', mailbox);
      //console.log('emails:', emails); 
      emails.forEach(email => {
         //console.log('email.read:', email.read, 'subject:', email.subject);
        // console.log('email.archived:', email.archived, 'email.subject:', email.subject); // <-- and this
        if (mailbox === 'sent' && email.archived) return;
        //if (mailbox === 'archive' && email.archived) return;

        const div = document.createElement('div');
        div.style.padding = '10px';
        div.style.marginBottom = '5px';
        div.style.border = '1px solid #ccc';
        div.style.borderRadius = '4px';
        div.style.cursor = 'pointer';
        div.style.overflow = 'hidden';
        div.style.textOverflow = 'ellipsis';
        div.style.whiteSpace = 'nowrap';
        div.style.backgroundColor = email.read ? '#d3d3d3' : '#fff9c4';
        div.style.fontWeight = email.read ? '400' : '700';
        //div.className = email.read ? 'email read' : 'email unread'; */
        div.innerHTML = `<strong>${email.sender}</strong> — ${email.subject} 
          <span style="float:right;">${email.timestamp}</span>`;
        div.addEventListener('click', () => {
        Object.assign(div.style, {
        backgroundColor: '#d3d3d3',  // grey when read
        fontWeight: '400'
        });
          if (mailbox === 'sent') {
            getSentEmail(email.id);
          } else {
            view_email(email.id);
          }
        });
        document.querySelector('#emails-view').append(div);
      });
    })  
    .catch(error => console.error('Error loading mailbox:', error));
}

function archive_email(email_id) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify({
      archived: true
    })
  })
}

function unarchive_email(email_id) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify({
      archived: false
    })
  })
}

function read_email(email_id) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify({
      read: true
    })
  })
  .then(response => {
    //console.log('read status:', response.status); 
})
}

function unread_email(email_id) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify({
      read: false
    })
  })
}

function reply_email(email_id) {
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {

    //Switch to compose view
      document.querySelector('#emails-view').style.display = 'none';
      document.querySelector('#compose-view').style.display = 'block';


      document.querySelector('#compose-recipients').value = email.sender;
      document.querySelector('#compose-subject').value = email.subject.startsWith('Re: ')
        ? email.subject
        : `Re: ${email.subject}`;
      document.querySelector('#compose-body').value = `\n\n--- On ${email.timestamp}, ${email.sender} wrote ---\n${email.body}`;
    });
}

function forward_email(email_id) {
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
    // Print email
   // console.log(email);
  });
}

function sendEmail(emailData) {
  
  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  if (!recipients || !subject || !body) {
    alert('Please fill in all fields.');
    return;
  }

  emailData = {
    recipients: recipients,
    subject: subject,
    body: body
  }

  fetch('/emails', {
    method: 'POST',
    headers: { 
    'Content-Type': 'application/json',
  'X-CSRFToken': getCSRFToken() 
},
    body: JSON.stringify(emailData)
  })
    .then(response => response.json())
    .then(result => {
      if (result.error) {
        alert(result.error);
        return;
      }
      //console.log('Email sent:', result);
      load_mailbox('sent');
    })
    .catch(error => {
      console.error('Error sending email:', error);
    });
}

function getCSRFToken() {
  const csrfCookie = document.cookie.match(/csrftoken=([^;]+)/);
  return csrfCookie ? csrfCookie[1] : null;
}



function getSentEmail(email_id) {
  fetch(`/emails/${email_id}`)
    .then(response => response.json())
    .then(email => {
      //console.log('email object:', email);        // check full email
      //console.log('archived:', email.archived);   // check archived state

      const archiveLabel = email.archived ? 'Unarchive' : 'Archive';

      document.querySelector('#emails-view').style.display = 'block';
      document.querySelector('#compose-view').style.display = 'none';

      document.querySelector('#emails-view').innerHTML = `
        <h3>Sent</h3>
        <p><strong>Recipients:</strong> ${email.recipients.join(', ')}</p>
        <p><strong>Subject:</strong> ${email.subject}</p>
        <p><strong>Body:</strong> ${email.body}</p>
        <button class="btn btn-sm btn-outline-primary" id="archive-btn">${archiveLabel}</button>
          <button class="btn btn-sm btn-outline-secondary" id="unread-btn">Mark as Unread</button>
          <button class="btn btn-sm btn-outline-primary" id="reply-btn">Reply</button>`;

     // console.log('archive button element:', document.querySelector('#archive-btn')); // check button exists

      // Mark as read
      fetch(`/emails/${email_id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ read: true })
      });

      // Archive / Unarchive
      const btn = document.querySelector('#archive-btn');
      if (btn) {
        btn.addEventListener('click', () => {
          fetch(`/emails/${email_id}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ archived: !email.archived })
          })
          .then(() => fetch(`/emails/${email_id}`))
          .then(response => response.json())
          .then(updated =>{ 
             load_mailbox(email.archived ? 'sent' : 'archive');
        });
      });
    }

    // Mark as Unread

    const unreadBtn = document.querySelector('#unread-btn');
if (unreadBtn) {
  unreadBtn.addEventListener('click', () => {
    fetch(`/emails/${email_id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify({ read: false })
    })
    .then(() => load_mailbox('sent'));
  });
}
    })

    .catch(error => {
      console.error('Error fetching sent email:', error);
    });

}

 function view_email(email_id) {
  fetch(`/emails/${email_id}`)
    .then(response => response.json())
    .then(email => {
      read_email(email_id);

      const currentUser = document.querySelector('h2').innerText;

      document.querySelector('#emails-view').style.display = 'block';
      document.querySelector('#compose-view').style.display = 'none';

      const archiveLabel = email.archived ? 'Unarchive' : 'Archive';
      const archiveButton = email.sender !== currentUser || email.archived ? `<button class="btn btn-sm btn-outline-primary" id="archive-btn">${archiveLabel}</button>`
  : '';

      document.querySelector('#emails-view').innerHTML = `
        <p><strong>From:</strong> ${email.sender}</p>
        <p><strong>To:</strong> ${email.recipients.join(', ')}</p>
        <p><strong>Subject:</strong> ${email.subject}</p>
        <p><strong>Timestamp:</strong> ${email.timestamp}</p>
        ${archiveButton}
        <button class="btn btn-sm btn-outline-secondary" id="unread-btn">Mark as Unread</button>
        <button class="btn btn-sm btn-outline-primary" id="reply-btn">Reply</button>
        <hr>
        <p>${email.body}</p>`;

        const btn = document.querySelector('#archive-btn');
      if (btn) {
        btn.addEventListener('click', () => {
          fetch(`/emails/${email_id}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ archived: !email.archived })
          })
          .then(() => fetch(`/emails/${email_id}`))
          .then(response => response.json())
          .then(updated =>{
            if (updated.archived) {
              load_mailbox('archive');
            } else {
              const currentUser = document.querySelector('h2').innerText;
              load_mailbox(currentUser === email.sender ? 'sent' : 'inbox');
            }
          });
        });
      }
      const unreadBtn = document.querySelector('#unread-btn');
if (unreadBtn) {
  unreadBtn.addEventListener('click', () => {
    fetch(`/emails/${email_id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify({ read: false })
    })
    .then(() => load_mailbox('inbox'));
  });
     
     const replyBtn = document.querySelector('#reply-btn');
if (replyBtn) {
  replyBtn.addEventListener('click', () => reply_email(email_id));
}
}
    });
}

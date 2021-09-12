
export default class UserAPI {
  call(userId, success, failed) {
    fetch(`/api/users/${userId}?format=json`)
      .then(res => res.json())
      .then(success)
      .catch(failed);
  }

  put(userId, data) {
    return fetch(`/api/users/${userId}`, {
      method: 'delete',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': window.django.csrf,
      },
      body: JSON.stringify(data),
    });
  }
};

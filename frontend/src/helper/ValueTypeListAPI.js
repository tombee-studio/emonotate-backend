
export default class ValueTypeListAPI {
  get(success, failed, page) {
    if(page) {
      fetch(`/api/valuetypes/?format=json&page=${page}`)
        .then(res => {
          return res.json();
        })
        .then(success)
        .catch(failed);
    } else {
      fetch('/api/valuetypes/?format=json')
      .then(res => res.json())
      .then(success)
      .catch(failed);
    }
  }

  getItem(id) {
    return fetch(`/api/valuetypes/${id}?format=json`)
      .then(res => {
        return res.json();
      });
  }

  history(success, failed, page) {
    if(page) {
      fetch(`/history/valuetypes/?format=json&page=${page}`)
        .then(res => {
          return res.json();
        })
        .then(success)
        .catch(failed);
    } else {
      fetch('/history/valuetypes/?format=json')
      .then(res => res.json())
      .then(success)
      .catch(failed);
    }
  }

  post(data) {
    return fetch('/api/valuetypes/?format=json', {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': window.django.csrf,
      },
      body: JSON.stringify(data)
    })
  }

  delete(item) {
    return fetch(`/api/valuetypes/${item}`, {
      method: 'delete',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': window.django.csrf,
      }
    })
  }
};

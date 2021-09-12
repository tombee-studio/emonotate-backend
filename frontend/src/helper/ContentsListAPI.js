
export default class ContentsListAPI {
  get(success, failed, page) {
    if(page) {
      fetch(`/api/contents/?format=json&page=${page}`)
        .then(res => {
          return res.json();
        })
        .then(success)
        .catch(failed);
    } else {
      fetch('/api/contents/?format=json')
      .then(res => res.json())
      .then(success)
      .catch(failed);
    }
  }

  history(success, failed, page) {
    if(page) {
      fetch(`/history/contents/?format=json&page=${page}`)
        .then(res => {
          return res.json();
        })
        .then(success)
        .catch(failed);
    } else {
      fetch('/history/contents/?format=json')
      .then(res => res.json())
      .then(success)
      .catch(failed);
    }
  }

  getItem(id, queries={
    'format': 'json'
  }) {
    const query = Object.keys(queries).map(key => `${key}=${queries[key]}`).join('&');
    return fetch(`/api/contents/${id}?${query}`)
      .then(res => {
          if(res.status != 200 && res.status != 201) throw res.message;
          return res.json();
      });
  }

  post(data) {
    return fetch('/api/contents/?format=json', {
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
    return fetch(`/api/contents/${item}`, {
      method: 'delete',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': window.django.csrf,
      }
    })
  }
};

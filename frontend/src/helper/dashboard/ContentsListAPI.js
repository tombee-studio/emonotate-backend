
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
};

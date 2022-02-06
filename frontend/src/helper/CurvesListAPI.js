
export default class CurvesListAPI {
  get(success, failed, page) {
    if(page) {
      fetch(`/api/curves/?format=json&page=${page}`)
        .then(res => {
          return res.json();
        })
        .then(success)
        .catch(failed);
    } else {
      fetch('/api/curves/?format=json')
      .then(res => res.json())
      .then(success)
      .catch(failed);
    }
  }

  history(page) {
    if(page) {
      return fetch(`/history/curves/?format=json&page=${page}`)
    } else {
      return fetch('/history/curves/?format=json')
    }
  }

  list(queries={
    'format': 'json'
  }) {
    const query = Object.keys(queries).map(key => `${key}=${queries[key]}`).join('&');
    return fetch(`/api/curves?${query}`)
      .then(res => {
          if(res.status != 200 && res.status != 201) throw res.message;
          return res.json();
      });
  }

  getItem(item) {
    return fetch(`/api/curves/${item}?format=json`)
      .then(res => {
        if(res.status == 200) return res.json();
        else throw "NOT FIND CURVE";
      });
  }

  create(data, queries={
    'format': 'json'
  }) {
    const query = Object.keys(queries).map(key => `${key}=${queries[key]}`).join('&');
    return fetch(`/api/curves/?${query}`, {
        method: 'post',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': window.django.csrf,
        },
        body: JSON.stringify(data)
      })
      .then(res => {
        if(res.status != 200 && res.status != 201) throw res;
        return res.json();
      });
  }

  delete(item) {
    return fetch(`/api/curves/${item}`, {
      method: 'delete',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': window.django.csrf,
      }
    })
  }
};

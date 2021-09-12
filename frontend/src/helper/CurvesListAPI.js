
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

  getItem(item) {
    return fetch(`/api/curves/${item}?format=json`)
      .then(res => {
        if(res.status == 200) return res.json();
        else throw "NOT FIND CURVE";
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


export default class RequestListAPI {
    get(queries = {}) {
        var query = Object.keys(queries).map(key => `${key}=${queries[key]}`).join('&');
        return fetch(`/api/requests/?${query}`)
            .then(res => {
                return res.json();
            });
    }

    delete(id, queries = {}) {
        var query = Object.keys(queries).map(key => `${key}=${queries[key]}`).join('&');
        return fetch(`/api/requests/${id}?${query}`,{
            method: 'delete',
            mode: 'cors',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': window.django.csrf,
            }});
    }
};
  
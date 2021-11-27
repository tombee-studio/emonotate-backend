export default class RequestListAPI {
    get(queries = {}) {
        var query = Object.keys(queries).map(key => `${key}=${queries[key]}`).join('&');
        return fetch(`/api/requests/?${query}`)
            .then(res => {
                return res.json();
            });
    }

    getItem(id, queries = {}) {
        var query = Object.keys(queries).map(key => `${key}=${queries[key]}`).join('&');
        return fetch(`/api/requests/${id}?${query}`)
            .then(res => {
                if(res.status != 200) throw res.message;
                return res.json();
            });
    }

    update(id, data = {}, queries = {format: 'json'}) {
        var query = Object.keys(queries).map(key => `${key}=${queries[key]}`).join('&');
        return fetch(`/api/requests/${id}/?${query}`, {
                method: 'put',
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.django.csrf,
                },
                body: JSON.stringify(data) })
            .then(res => {
                if(res.status != 200) throw res.message;
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
  

export default class RequestListAPI {
    get(queries = {}) {
        var query = Object.keys(queries).map(key => `${key}=${queries[key]}`).join('&');
        return fetch(`/api/requests/?${query}`)
            .then(res => {
                return res.json();
            });
    }
};
  
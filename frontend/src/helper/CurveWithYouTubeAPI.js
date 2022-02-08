
export default class CurveWithYouTubeAPI {
  create(data, queries={
    'format': 'json'
  }) {
    const query = Object.keys(queries).map(key => `${key}=${queries[key]}`).join('&');
    return fetch(`/api/curves_with_youtube/?${query}`, {
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
};


export default class CurvesListAPI {
  call(success, failed, page) {
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
};

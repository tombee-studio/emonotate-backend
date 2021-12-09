export default class AuthenticateAPI {
    login(data) {
      console.log(data);
      return fetch('/api/login/?format=json', {
        method: 'post',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': window.django.csrf,
        },
        body: JSON.stringify(data)
      }).then(res => {
          if (res.status == 200) return res.json();
          else throw res.json()
      });
    }

    logout() {
        return fetch('/api/logout/?format=json', {
          method: 'post',
          mode: 'cors',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.django.csrf,
          }
        }).then(res => {
            return res.json()
        })
      }
  };
  
import React from 'react';
import Loader from 'react-loader-spinner';
import axios from 'axios';
import './App.scss';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      file: undefined,
    };
    this.onChange = this.onChange.bind(this);
    this.fileUpload = this.fileUpload.bind(this);
    this.check = this.check.bind(this);
  }
  onChange(e) {
    this.fileUpload(e.target.files[0]);
  }
  check() {
    console.log('checking');
    const url =
      'https://us-central1-graphical-envoy-287420.cloudfunctions.net/check';
    axios
      .get(url, { params: { file: this.state.file.outname } })
      .then(res => {
        console.log('res', res);
        if (res.status === 200) {
          this.setState({ url: res.data});
          clearInterval(this.state.file.interval);
        }
        return '';
      })
      .catch(err => console.log('err', err));
  }
  fileUpload(file) {
    const url =
      'https://us-central1-graphical-envoy-287420.cloudfunctions.net/upload';
    const formData = new FormData();
    formData.append('file', file);
    const config = {
      headers: {
        'content-type': 'multipart/form-data',
      },
    };
    axios
      .post(url, formData, config)
      .then(res => {
        let f = {
          name: file.name,
          outname: res.data,
          interval: setInterval(this.check, 3000),
        };
        this.setState({ file: f });
      })
      .catch(err => console.log(err));
  }

  render() {
    let processing = '';
    if (this.state.file) {
      if (this.state.url) {
        processing = (
          <div className='file'>
            <p className='filename'>{this.state.file.name}</p>
            <a className='link' href={this.state.url}>
              Download
            </a>
          </div>
        );
      } else {
        processing = (
          <div className='file'>
            <p className='filename'>{this.state.file.name}</p>
            <Loader
              type='ThreeDots'
              width={200}
              height={200}
              color='#FFD166'></Loader>
          </div>
        );
      }
    }

    return (
      <div>
        <div className='navbar'>
          <h1>smoothr</h1>
        </div>
        <p>Upload MP4 to smooth the FPS!</p>
        <form>
          <label class='custom-file-upload'>
            <input type='file' onChange={this.onChange} />
            Upload
          </label>
        </form>
        {processing}
      </div>
    );
  }
}

export default App;

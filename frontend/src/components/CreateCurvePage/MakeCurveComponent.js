import React from "react";
import { DataGrid } from '@material-ui/data-grid';
import Helmet from 'react-helmet';
import { Grid } from "@material-ui/core";
import videojs from 'video.js'
import "video.js/dist/video-js.css"

class MakeCurveComponent extends React.Component {
  constructor(props) {
    super(props);

    const { content } = this.props;
    this.CONSTANT = {
      video: 'video',
      chart: 'chart',
    };
    this.createEmotionalArcInputField = this.createEmotionalArcInputField.bind(this);
    this.videoJsOptions = {
      autoplay: true,
      controls: true,
      sources: [{
        src: content.url,
        type: 'video/mp4'
      }]
    }
  }

  createEmotionalArcInputField() {
    const { valueType } = this.props;
    const value_type = valueType;
    if(value_type.axis_type == 1){
      var axis = {
          maxValue: 1,
          minValue: -1,
          centralValue: 0,
      };
    }
    else if(value_type.axis_type == 2) {
      var axis = {
        maxValue: 1,
        minValue: 0,
        centralValue: 0,
      };
    }
    axis.title = value_type.title;
    this.inputField = new EmotionalArcField(this.chartNode, this.videoNode, axis, { 
        'r': 12,
        'color': 'black',
    });
    this.inputField.onVideoLoaded = () => {
      const dataset = [
        {
          id: 0,
          x: 0.0,
          y: 0.0,
          axis: 'v',
          type: 'fixed',
          text:   "",
          reason: "",
        }, {
          id: 1,
          x: this.inputField.duration,
          y: 0.0,
          axis: 'v',
          type: 'fixed',
          text:   "",
          reason: "",
      }];
      if(this.inputField) {
        this.inputField.load(dataset);
      }
    };
  }

  componentDidMount() {
    this.player = videojs(this.videoNode, this.videoJsOptions);

    this.player.on('loadedmetadata', () => {
      this.createEmotionalArcInputField();
    });
  }

  render() {
    const columns = [
      {
        field: 'id',
        headerName: '通し番号',
        width: 30
      }, 
      {
        field: 'x',
        headerName: '時間',
        width: 30
      }, {
        field: 'y',
        headerName: '値',
        width: 30
      }, {
        field: 'text',
        headerName: '説明',
        width: 200
      }
    ];
    return (
      <div>
        <Helmet>
          <script src="/static/users/js/emotional-arc-input-field.js" />
          <link rel="stylesheet" href="/static/users/css/emotional-arc-input-field.css" />
          <script src="/static/users/d3/d3.min.js" />
        </Helmet>
        <Grid container>
          <Grid item xs={7}>
            <div data-vjs-player>
              <video
                id={ this.CONSTANT.video }
                ref={ node => this.videoNode = node }
                height={300}
                className="video-js" />
            </div>
          </Grid>
          <Grid item xs={12}>
            <svg
              id={ this.CONSTANT.chart }
              ref={node => this.chartNode = node}
              version="1.1"
              width="100%"
              height="280px" />
          </Grid>
        </Grid>
      </div>
    );
  }
};

export default MakeCurveComponent;

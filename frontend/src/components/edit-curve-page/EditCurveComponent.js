import React from "react";
import { DataGrid } from '@material-ui/data-grid';
import Helmet from 'react-helmet';
import { Button, Grid, Select, Box } from "@material-ui/core";
import UserAPI from "../../helper/UserAPI";
import videojs from 'video.js';
import "video.js/dist/video-js.css";

import EmotionalArcField from '../../helper/emotional-arc-input-field';

class MakeCurveComponent extends React.Component {
  constructor(props) {
    super(props);
    const { content, counts } = this.props;
    this.api = new UserAPI();
    this.content = content;
    this.counts = counts;
    this.CONSTANT = {
      video: 'video',
      chart: 'chart',
    };
    this.createEmotionalArcInputField = this.createEmotionalArcInputField.bind(this);
    this.videoJsOptions = {
      autoplay: false,
      controls: true,
      sources: [{
        src: content.url,
        type: content.data_type
      }]
    }
    this.state = {
      dataset: [],
      isLoadedVideo: false,
      isLoadedScript: false,
    };
  }

  loadedAll() {
    if(this.state.isLoadedScript && this.state.isLoadedVideo) {
      this.createEmotionalArcInputField();
    }
  }

  createEmotionalArcInputField() {
    const { values, valueType } = this.props;
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
    while (this.chartNode.lastChild) {
      this.chartNode.removeChild(this.chartNode.lastChild);
    }
    this.inputField = new EmotionalArcField(this.chartNode, this.videoNode, axis, { 
        'r': 12,
        'color': 'black',
    });
    this.inputField.onVideoLoaded = () => {
        return
    }
    this.inputField.OnInit();
    const dataset = values;
    this.inputField.load(dataset);
  }

  componentDidMount() {
    this.player = videojs(this.videoNode, this.videoJsOptions);
    this.player.ready(() => {
      this.player.on('loadedmetadata', () => {
        this.setState({
          isLoadedVideo: true
        });
        this.loadedAll();
      });
    });
    EmotionalArcField.loadScript("/static/users/d3/d3.min.js", () => { 
      this.setState({
        isLoadedScript: true
      });
      this.loadedAll();
    });
  }

  render() {
    const { valueType } = this.props;
    if(valueType) {
      this.value_type = valueType;
    }
    const { user } = window.django;
    return (
      <Box m={2}>
        <Helmet>
          <script src="/static/users/js/emotional-arc-input-field.js" />
          <link rel="stylesheet" href="/static/users/css/emotional-arc-input-field.css" />
          <script src="/static/users/d3/d3.min.js" />
        </Helmet>
        <Grid container>
          <Grid item xs={5}>
            <div data-vjs-player>
              <video
                id={ this.CONSTANT.video }
                ref={ node => this.videoNode = node }
                height={280}
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
          {/* <Grid item>
            <Button
              color="primary"
              variant="contained"
              onClick={(e) => {
              this.api.call(user.id, (user) => {
                this.inputField.update(user, this.content, this.value_type, roomName, '1.1');
              }, (err) => { console.log(err.body); });
            }}>
              感情曲線を追加
            </Button>
          </Grid> */}
        </Grid>
      </Box>
    );
  }
};

export default MakeCurveComponent;

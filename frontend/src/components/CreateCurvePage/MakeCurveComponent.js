import React from "react";
import { Box } from "@material-ui/core";
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
    var inputField = new EmotionalArcField(this.chartNode, this.videoNode, axis, { 
        'r': 12,
        'color': 'black',
    });
    inputField.onVideoLoaded = () => {
        var dataset = [];
        dataset.push({
            x: 0.0,
            y: 0.0,
            axis: 'v',
            type: 'fixed',
            text:   "",
            reason: "",
        });
        dataset.push({
            x: inputField.duration,
            y: 0.0,
            axis: 'v',
            type: 'fixed',
            text:   "",
            reason: "",
        });
        inputField.load(dataset);
    };
  }

  componentDidMount() {
    this.player = videojs(this.videoNode, this.videoJsOptions);

    this.player.on('loadedmetadata', () => {
      this.createEmotionalArcInputField();
    });
  }

  render() {
    return (
      <div>
        <Grid container>
          <Grid item>
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

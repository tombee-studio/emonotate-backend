import React from "react";
import { Box } from "@material-ui/core";
import { Grid } from "@material-ui/core";
import { Helmet } from "react-helmet";

class MakeCurveComponent extends React.Component {
  constructor(props) {
    super(props);

    this.createEmotionalArcInputField = this.createEmotionalArcInputField.bind(this);
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
    window.onload = () => {
      this.createEmotionalArcInputField();
    };
  }

  render() {
    const { content } = this.props;
    return (
      <Box m={2}>
        <Helmet>
          <script src="/static/users/js/emotional-arc-input-field.js" />
          <link rel="stylesheet" href="/static/users/css/emotional-arc-input-field.css" />
          <script src="/static/users/d3/d3.min.js" />
        </Helmet>
        <Grid container>
          <Grid item>
            <video
              id="video"
              ref={node => this.videoNode = node}
              src={content.url}
              height="320px"
              type="video/mp4"
              controls />
          </Grid>
          <Grid item xs={12}>
            <svg
              id="chart"
              ref={node => this.chartNode = node}
              version="1.1"
              width="100%"
              height="280px" />
          </Grid>
        </Grid>
      </Box>
    );
  }
};

export default MakeCurveComponent;

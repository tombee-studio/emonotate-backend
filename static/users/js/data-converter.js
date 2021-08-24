const DataConverter = {}

DataConverter.MAP = {
    '0.0.0': '0.1.0',
    '0.0.1': '0.1.0',
    '0.0.2': '0.1.0',
    '0.1.0': '0.1.1',
}

DataConverter.init = function(video) {
    this.video = video;
    DataConverter.converters = {};
    DataConverter.converters['0.0.0'] = data => {
        const time = data['time'];
        const ps = data.values.map(point => {
            return {
                x:      point.progress * time,
                y:      point.value,
                text:   point.text || "",
                reason: point.reason || "",
                axis:   'vh',
                type:   'custom',
            };
        });
        ps[0].axis = 'v';
        ps[0].type = 'fixed';
        ps[ps.length - 1].axis = 'v';
        ps[ps.length - 1].type = 'fixed';
        return ps;
    };

    DataConverter.converters['0.0.1'] = data => {
        const sortedData = data.sort((p1, p2) => {
            if(p1.x > p2.x) return 1;
            else if(p1.x < p2.x) return -1;
            else 0
        });
        const ps = sortedData.map(p => {
            return {
                x:      p.progress * video.duration,
                y:      p.value,
                text:   p.text || "",
                reason: p.reason || "",
                axis:   'vh',
                type:   'custom',
            };
        });
        ps[0].axis = 'v';
        ps[0].type = 'fixed';
        ps[ps.length - 1].axis = 'v';
        ps[ps.length - 1].type = 'fixed';
        return ps;
    };
    
    DataConverter.converters['0.0.2'] = data => {
        const sortedData = data.sort((p1, p2) => {
            if(p1.x > p2.x) return 1;
            else if(p1.x < p2.x) return -1;
            else 0
        });
        const ps = sortedData.map(p => {
            return {
                x:      p.x,
                y:      p.value,
                text:   p.text || "",
                reason: p.reason || "",
                axis:   'vh',
                type:   'custom',
            };
        });
        ps[0].axis = 'v';
        ps[0].type = 'fixed';
        ps[ps.length - 1].axis = 'v';
        ps[ps.length - 1].type = 'fixed';
        return ps;
    };

    DataConverter.converters['0.1.0'] = data => {
        const ps = data.map(p => {
            return {
                x:      p.x,
                y:      p.y,
                text:   p.text || "",
                reason: p.reason || "",
                axis:   'vh',
                type:   'custom',
            };
        });
        ps[0].axis = 'v';
        ps[0].type = 'fixed';
        ps[ps.length - 1].axis = 'v';
        ps[ps.length - 1].type = 'fixed';
        return ps;
    };
}

DataConverter.convert = function (data, originalVersion, targetVersion) {
    if(originalVersion == targetVersion) return data;
    if(!originalVersion in DataConverter.MAP) 
        throw `can't convert from ${originalVersion}`;
    const targetData = DataConverter.converters[originalVersion](data);
    if(DataConverter.MAP[originalVersion] == targetVersion) return targetData;
    else return DataConverter.convert(targetData, DataConverter.MAP[originalVersion], targetVersion);
}

"use strict";

class GeoSearch
{
    constructor(parentId){

        let self = this;
        this.parentId = parentId;

        $('#'+parentId).append(
                    `
                    <div id="${parentId}-searchselected" class="w3-container"></div>
                    <div id="${parentId}-searchinput" class="w3-container">
                        <span class="w3-badge w3-green">+</span>&nbsp;
                        <input type="text" name="${parentId}-placesearch"></input></div>
                    <div id="${parentId}-searchsuggestions" style="position: absolute; z-index:999;"></div>
                    `
            );

        $(`input[name=${parentId}-placesearch]`) .keyup(_.debounce(()=>self.search(), 500));

        this.searchSelected = [];
        this.searchData = {};
    }

    search(){
        let self = this;
        let pId = self.parentId;

        let searchstring = $(`input[name=${pId}-placesearch]`).val();

        if (searchstring.length>1)
        {
        
            $.getJSON('/api/searchplaces?string='+searchstring, function(data) {

                self.searchData = {};
                data.forEach(function(entry){

                    let geonameid = entry[0];
                    let text = self.getLocationSuggestionDiv(entry);
                    self.searchData[geonameid] = entry;

                    $(`#${pId}-searchsuggestions`).append(text);
                    $(`#${pId}-suggestion-${geonameid}`).bind("click", ()=>self.locationSelected(geonameid));
                });

            });
            
        }
        else
        {
            $(`#${pId}-searchsuggestions`).html('');
        }

    }

    locationSelected(geonameid) {

        let self = this;
        let pId = self.parentId;

        if (self.searchSelected.indexOf(geonameid) >= 0)
        {
            $(`#${pId}-searchsuggestions`).html("");
            $(`input[name=${pId}-placesearch]`).val('');
        
            return;
        }

        let entry = self.searchData[geonameid];
        self.searchSelected.push(geonameid);

        // get a div that displays the selected
        let selected = self.getLocationSelectedDiv(entry);
        
        // append it to the selection div and delete the search suggestions
        $(`#${pId}-searchselected`).append(selected);
        $(`#${pId}-searchsuggestions`).html("");
        $(`input[name=${pId}-placesearch]`).val('');

        // add functionality to delete this entry
        $(`#${pId}-deletelocation-${geonameid}`).bind("click", ()=>self.deleteSelected(geonameid));
    }

    getLocationSelectedDiv(entry) {

        let self = this;
        let pId = this.parentId;

        let geonameid = entry[0];
        let asciiname = entry[1];
        let countrycode = entry[2];
        let country = entry[3];
        let fcode = entry[4];
        let fcodeDescription = entry[5];
        let fcodeExplanation = entry[6];
        let population = entry[7];
        let name = entry[8];

        let humanformat = d3.format(".2s");

        let text = `<div id="${pId}-selectedlocation-${geonameid}" class="w3-margin-bottom w3-animate-bottom">`;

        text += `<span class="w3-badge w3-red pointer w3-small" id="${pId}-deletelocation-${geonameid}">x</span> &nbsp;`;

        text += `<span class="w3-margin-bottom w3-light-grey w3-padding">`;


        if ((countrycode.length == 2))
        {
            text += `<span class="flag-icon flag-icon-${countrycode.toLowerCase()}"></span>&nbsp;`;
        }

        text += `<span>${name}</span>&nbsp;`;

        text += "</span>";

        return text;

    }

    deleteSelected(geonameid) {
        let self = this;
        let pId = this.parentId;

        $(`#${pId}-selectedlocation-${geonameid}`).fadeOut(150);

        setTimeout(() => $(`#${pId}-selectedlocation-${geonameid}`).remove(), 500);
        self.searchSelected.splice(self.searchSelected.indexOf(geonameid),1);
    }

    getLocationSuggestionDiv(entry) {
        let self = this;
        let pId = this.parentId;

        let geonameid = entry[0];
        let asciiname = entry[1];
        let countrycode = entry[2];
        let country = entry[3];
        let fcode = entry[4];
        let fcodeDescription = entry[5];
        let fcodeExplanation = entry[6];
        let population = entry[7];
        let name = entry[8];

        let humanformat = d3.format(".2s");

        if (name == '')
        {
            name = asciiname;
            entry[8] = asciiname;
        }
        
        let text = `
                        <div class="w3-container 
                                    w3-hover-light-grey 
                                    w3-border
                                    w3-white
                                    pointer
                                    " 
                             id="${pId}-suggestion-${geonameid}"
                   >`;

        text += `<p>`;

        if ((countrycode.length == 2) && (fcode == 'PCLI'))
        {
            text += `<span class="flag-icon flag-icon-${countrycode.toLowerCase()}"></span>&nbsp;`;
        }

        text += `${name}`;

        if (asciiname!=name)
        {
            text += '&nbsp;<span class="w3-small">';
            text += `(${asciiname})`;
            text += '</span>';
        }

        if ((country !== null) && (fcode != 'PCLI'))
        {
            text += '<br/><span class="w3-small">';
            text += `<span class="flag-icon flag-icon-${countrycode.toLowerCase()}"></span>&nbsp;`;
            text += country + ' (' + countrycode + ')';
            text += '</span>';
        }

        if (fcode != null)
        {
            text += `<br/><span class="w3-small w3-text-grey" alt="${fcodeExplanation}">${fcode}: ${fcodeDescription},&nbsp;</span>`
        }

        text += `<span class="w3-small w3-text-grey">population: `+humanformat(population)+`</span>`;

        text += '</p>';

        text += `</div>`;

        return text;

    }

}

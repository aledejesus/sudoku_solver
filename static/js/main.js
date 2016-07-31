// console.log("REACT SCRIPT");

var NumberInput = React.createClass({
    render: function(){
        return (
            <div style={{fontSize: 30 + "px", position: "absolute"}}>
              <input type="number" className="number_input" min="1" max="9"/>
            </div>
        );
    }
});

ReactDOM.render(
  <NumberInput/>,
  document.getElementById('0_00')
);

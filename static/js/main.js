// console.log("REACT SCRIPT");

var NumberInput = React.createClass({
  componentDidMount: function(){
    ReactDOM.findDOMNode(this.refs.number_input).focus(); 
  },
  render: function(){
    return (
      <div style={{fontSize: 30 + "px", position: "absolute"}}>
        <input type="number" ref="number_input" className="number_input form-control" min="1" max="9"/>
      </div>
    );
  }
});

ReactDOM.render(
  <NumberInput/>,
  document.getElementById('0_00')
);

$(function(){
	var toCollapse = $("div.collapse[rel]");
	
	//var checkboxRels = $()
	var radioRels = $()
	var plainRels = $()
	
	for (var i=0;i<toCollapse.length;i++) {
		toggler = $('#'+toCollapse[i].getAttribute('rel'))[0]
		if (toggler.type == 'radio'){
			radioRels = radioRels.add(':radio[name='+toggler.name+']')
		//} else if(toggler.type == 'checkbox'){
		//	checkboxRels = checkboxRels.add(toggler)
		} else {
			plainRels = plainRels.add(toggler)
		}
	}
	
	toHide = radioRels.filter(':not(:checked)').add(plainRels)
	for(i=0;i<toHide.length;i++){
		toCollapse.filter('[rel='+toHide[i].id+']').hide()
	}
	
	radioRels.change(function(){
		related = $(':radio[name='+this.name+']');
		for(var i=0;i<related.length;i++){
			if(related[i] == this) continue;
			toCollapse.filter('[rel='+related[i].id+']').slideUp('medium')
		}
		toCollapse.filter('[rel='+this.id+']').slideDown('medium')
	})
	
	plainRels.click(function(){
			toCollapse.filter('[rel='+this.id+']').slideToggle('medium')
	})
})
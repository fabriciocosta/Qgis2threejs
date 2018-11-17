
var GIX = Object.assign( Q3D, {
	sceneFog: function( fogColor, near, far ) {
		var _near = near | 0.0025;
		var _far = far | 2000.0;
		var _bgcolor = new THREE.Color(1.0,1.0,1.0);
		var _fogColor = fogColor | _bgcolor;
		console.log("fogColor:",_fogColor," near:",_near,"far:",_far);
		this.application.scene.autoUpdate = true;
		this.application.scene.background = _fogColor;
		this.application.scene.fog = new THREE.Fog( _fogColor, _near, _far);
	},
	getLayerByName: function( name ) {
		var _ret_layer = {};
		this.application.project.layers.forEach(function(layer) {
			if (layer.name == name ) {
				_ret_layer = layer;
			}
		});
		return _ret_layer;
	},
	scaleLayer: function( layer, sx, sy, sz ) {
		for (var i = 0, l = layer.objectGroup.children.length; i < l; i++) {
			var Mesh = layer.objectGroup.children[i];
			Mesh.scale.x = sx;
			Mesh.scale.y = sy;
			Mesh.scale.z = sz;
		}
		layer.updateMatrixWorld();
	},
	moveLayer: function( layer, mx, my, mz ) {
		for (var i = 0, l = layer.objectGroup.children.length; i < l; i++) {
			var Mesh = layer.objectGroup.children[i];
			Mesh.position.x+= mx;
			Mesh.position.y+= my;
			Mesh.position.z+= mz;
		}
		layer.updateMatrixWorld();
	},
	colorLayer: function( layer, cr, cg, cb, ar, ag, ab, er, eg, eb) {
		layer.materials.forEach(function (m) {
      //m.m.transparent = Boolean(m.t) || (opacity < 1);
      //m.m.opacity = a;
			if (cr!==false && cg!==false && cb!==false) {
				m.m.color =  new THREE.Color(cr, cg, cb);
			}
			if (ar!==false && ag!==false && ab!==false) {
				m.m.ambient =  new THREE.Color(ar, ag, ab);
			}
			if (er!==false && eg!==false && eb!==false) {
				m.m.emissive =  new THREE.Color(er, eg, eb);
			}
    });
	},
	getSelectedObject: function() {
		return this.applicatino.highlightObject;
	}

});



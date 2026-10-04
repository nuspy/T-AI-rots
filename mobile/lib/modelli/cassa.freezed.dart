// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'cassa.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$PrezzoRinnovo {

 int get listino; int get conRinnovo; num get sconto;
/// Create a copy of PrezzoRinnovo
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PrezzoRinnovoCopyWith<PrezzoRinnovo> get copyWith => _$PrezzoRinnovoCopyWithImpl<PrezzoRinnovo>(this as PrezzoRinnovo, _$identity);

  /// Serializes this PrezzoRinnovo to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as PrezzoRinnovo;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PrezzoRinnovo&&(identical(other.listino, _this.listino) || other.listino == _this.listino)&&(identical(other.conRinnovo, _this.conRinnovo) || other.conRinnovo == _this.conRinnovo)&&(identical(other.sconto, _this.sconto) || other.sconto == _this.sconto));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as PrezzoRinnovo;
  return Object.hash(runtimeType,_this.listino,_this.conRinnovo,_this.sconto);
}

@override
String toString() {
  final _this = this as PrezzoRinnovo;
  return 'PrezzoRinnovo(listino: ${_this.listino}, conRinnovo: ${_this.conRinnovo}, sconto: ${_this.sconto})';
}


}

/// @nodoc
abstract mixin class $PrezzoRinnovoCopyWith<$Res>  {
  factory $PrezzoRinnovoCopyWith(PrezzoRinnovo value, $Res Function(PrezzoRinnovo) _then) = _$PrezzoRinnovoCopyWithImpl;
@useResult
$Res call({
 int listino, int conRinnovo, num sconto
});




}
/// @nodoc
class _$PrezzoRinnovoCopyWithImpl<$Res>
    implements $PrezzoRinnovoCopyWith<$Res> {
  _$PrezzoRinnovoCopyWithImpl(this._self, this._then);

  final PrezzoRinnovo _self;
  final $Res Function(PrezzoRinnovo) _then;

/// Create a copy of PrezzoRinnovo
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? listino = null,Object? conRinnovo = null,Object? sconto = null,}) {
  return _then(PrezzoRinnovo(
listino: null == listino ? _self.listino : listino // ignore: cast_nullable_to_non_nullable
as int,conRinnovo: null == conRinnovo ? _self.conRinnovo : conRinnovo // ignore: cast_nullable_to_non_nullable
as int,sconto: null == sconto ? _self.sconto : sconto // ignore: cast_nullable_to_non_nullable
as num,
  ));
}

}


/// Adds pattern-matching-related methods to [PrezzoRinnovo].
extension PrezzoRinnovoPatterns on PrezzoRinnovo {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PrezzoRinnovo value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PrezzoRinnovo() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PrezzoRinnovo value)  $default,){
final _that = this;
switch (_that) {
case _PrezzoRinnovo():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PrezzoRinnovo value)?  $default,){
final _that = this;
switch (_that) {
case _PrezzoRinnovo() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int listino,  int conRinnovo,  num sconto)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PrezzoRinnovo() when $default != null:
return $default(_that.listino,_that.conRinnovo,_that.sconto);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int listino,  int conRinnovo,  num sconto)  $default,) {final _that = this;
switch (_that) {
case _PrezzoRinnovo():
return $default(_that.listino,_that.conRinnovo,_that.sconto);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int listino,  int conRinnovo,  num sconto)?  $default,) {final _that = this;
switch (_that) {
case _PrezzoRinnovo() when $default != null:
return $default(_that.listino,_that.conRinnovo,_that.sconto);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _PrezzoRinnovo implements PrezzoRinnovo {
  const _PrezzoRinnovo({required this.listino, required this.conRinnovo, this.sconto = 0});
  factory _PrezzoRinnovo.fromJson(Map<String, dynamic> json) => _$PrezzoRinnovoFromJson(json);

@override final  int listino;
@override final  int conRinnovo;
@override@JsonKey() final  num sconto;

/// Create a copy of PrezzoRinnovo
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PrezzoRinnovoCopyWith<_PrezzoRinnovo> get copyWith => __$PrezzoRinnovoCopyWithImpl<_PrezzoRinnovo>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PrezzoRinnovoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _PrezzoRinnovo&&(identical(other.listino, listino) || other.listino == listino)&&(identical(other.conRinnovo, conRinnovo) || other.conRinnovo == conRinnovo)&&(identical(other.sconto, sconto) || other.sconto == sconto));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,listino,conRinnovo,sconto);
}

@override
String toString() {
    return 'PrezzoRinnovo(listino: $listino, conRinnovo: $conRinnovo, sconto: $sconto)';
}


}

/// @nodoc
abstract mixin class _$PrezzoRinnovoCopyWith<$Res> implements $PrezzoRinnovoCopyWith<$Res> {
  factory _$PrezzoRinnovoCopyWith(_PrezzoRinnovo value, $Res Function(_PrezzoRinnovo) _then) = __$PrezzoRinnovoCopyWithImpl;
@override @useResult
$Res call({
 int listino, int conRinnovo, num sconto
});




}
/// @nodoc
class __$PrezzoRinnovoCopyWithImpl<$Res>
    implements _$PrezzoRinnovoCopyWith<$Res> {
  __$PrezzoRinnovoCopyWithImpl(this._self, this._then);

  final _PrezzoRinnovo _self;
  final $Res Function(_PrezzoRinnovo) _then;

/// Create a copy of PrezzoRinnovo
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? listino = null,Object? conRinnovo = null,Object? sconto = null,}) {
  return _then(_PrezzoRinnovo(
listino: null == listino ? _self.listino : listino // ignore: cast_nullable_to_non_nullable
as int,conRinnovo: null == conRinnovo ? _self.conRinnovo : conRinnovo // ignore: cast_nullable_to_non_nullable
as int,sconto: null == sconto ? _self.sconto : sconto // ignore: cast_nullable_to_non_nullable
as num,
  ));
}


}


/// @nodoc
mixin _$PrezziPiano {

 PrezzoRinnovo get mensile; PrezzoRinnovo? get annuale; int? get provaAnnuale;
/// Create a copy of PrezziPiano
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PrezziPianoCopyWith<PrezziPiano> get copyWith => _$PrezziPianoCopyWithImpl<PrezziPiano>(this as PrezziPiano, _$identity);

  /// Serializes this PrezziPiano to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as PrezziPiano;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PrezziPiano&&(identical(other.mensile, _this.mensile) || other.mensile == _this.mensile)&&(identical(other.annuale, _this.annuale) || other.annuale == _this.annuale)&&(identical(other.provaAnnuale, _this.provaAnnuale) || other.provaAnnuale == _this.provaAnnuale));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as PrezziPiano;
  return Object.hash(runtimeType,_this.mensile,_this.annuale,_this.provaAnnuale);
}

@override
String toString() {
  final _this = this as PrezziPiano;
  return 'PrezziPiano(mensile: ${_this.mensile}, annuale: ${_this.annuale}, provaAnnuale: ${_this.provaAnnuale})';
}


}

/// @nodoc
abstract mixin class $PrezziPianoCopyWith<$Res>  {
  factory $PrezziPianoCopyWith(PrezziPiano value, $Res Function(PrezziPiano) _then) = _$PrezziPianoCopyWithImpl;
@useResult
$Res call({
 PrezzoRinnovo mensile, PrezzoRinnovo? annuale, int? provaAnnuale
});


$PrezzoRinnovoCopyWith<$Res> get mensile;$PrezzoRinnovoCopyWith<$Res>? get annuale;

}
/// @nodoc
class _$PrezziPianoCopyWithImpl<$Res>
    implements $PrezziPianoCopyWith<$Res> {
  _$PrezziPianoCopyWithImpl(this._self, this._then);

  final PrezziPiano _self;
  final $Res Function(PrezziPiano) _then;

/// Create a copy of PrezziPiano
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? mensile = null,Object? annuale = freezed,Object? provaAnnuale = freezed,}) {
  return _then(PrezziPiano(
mensile: null == mensile ? _self.mensile : mensile // ignore: cast_nullable_to_non_nullable
as PrezzoRinnovo,annuale: freezed == annuale ? _self.annuale : annuale // ignore: cast_nullable_to_non_nullable
as PrezzoRinnovo?,provaAnnuale: freezed == provaAnnuale ? _self.provaAnnuale : provaAnnuale // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}
/// Create a copy of PrezziPiano
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PrezzoRinnovoCopyWith<$Res> get mensile {
  
  return $PrezzoRinnovoCopyWith<$Res>(_self.mensile, (value) {
    return _then(_self.copyWith(mensile: value));
  });
}/// Create a copy of PrezziPiano
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PrezzoRinnovoCopyWith<$Res>? get annuale {
    if (_self.annuale == null) {
    return null;
  }

  return $PrezzoRinnovoCopyWith<$Res>(_self.annuale!, (value) {
    return _then(_self.copyWith(annuale: value));
  });
}
}


/// Adds pattern-matching-related methods to [PrezziPiano].
extension PrezziPianoPatterns on PrezziPiano {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PrezziPiano value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PrezziPiano() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PrezziPiano value)  $default,){
final _that = this;
switch (_that) {
case _PrezziPiano():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PrezziPiano value)?  $default,){
final _that = this;
switch (_that) {
case _PrezziPiano() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( PrezzoRinnovo mensile,  PrezzoRinnovo? annuale,  int? provaAnnuale)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PrezziPiano() when $default != null:
return $default(_that.mensile,_that.annuale,_that.provaAnnuale);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( PrezzoRinnovo mensile,  PrezzoRinnovo? annuale,  int? provaAnnuale)  $default,) {final _that = this;
switch (_that) {
case _PrezziPiano():
return $default(_that.mensile,_that.annuale,_that.provaAnnuale);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( PrezzoRinnovo mensile,  PrezzoRinnovo? annuale,  int? provaAnnuale)?  $default,) {final _that = this;
switch (_that) {
case _PrezziPiano() when $default != null:
return $default(_that.mensile,_that.annuale,_that.provaAnnuale);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _PrezziPiano implements PrezziPiano {
  const _PrezziPiano({required this.mensile, this.annuale, this.provaAnnuale});
  factory _PrezziPiano.fromJson(Map<String, dynamic> json) => _$PrezziPianoFromJson(json);

@override final  PrezzoRinnovo mensile;
@override final  PrezzoRinnovo? annuale;
@override final  int? provaAnnuale;

/// Create a copy of PrezziPiano
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PrezziPianoCopyWith<_PrezziPiano> get copyWith => __$PrezziPianoCopyWithImpl<_PrezziPiano>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PrezziPianoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _PrezziPiano&&(identical(other.mensile, mensile) || other.mensile == mensile)&&(identical(other.annuale, annuale) || other.annuale == annuale)&&(identical(other.provaAnnuale, provaAnnuale) || other.provaAnnuale == provaAnnuale));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,mensile,annuale,provaAnnuale);
}

@override
String toString() {
    return 'PrezziPiano(mensile: $mensile, annuale: $annuale, provaAnnuale: $provaAnnuale)';
}


}

/// @nodoc
abstract mixin class _$PrezziPianoCopyWith<$Res> implements $PrezziPianoCopyWith<$Res> {
  factory _$PrezziPianoCopyWith(_PrezziPiano value, $Res Function(_PrezziPiano) _then) = __$PrezziPianoCopyWithImpl;
@override @useResult
$Res call({
 PrezzoRinnovo mensile, PrezzoRinnovo? annuale, int? provaAnnuale
});


@override $PrezzoRinnovoCopyWith<$Res> get mensile;@override $PrezzoRinnovoCopyWith<$Res>? get annuale;

}
/// @nodoc
class __$PrezziPianoCopyWithImpl<$Res>
    implements _$PrezziPianoCopyWith<$Res> {
  __$PrezziPianoCopyWithImpl(this._self, this._then);

  final _PrezziPiano _self;
  final $Res Function(_PrezziPiano) _then;

/// Create a copy of PrezziPiano
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? mensile = null,Object? annuale = freezed,Object? provaAnnuale = freezed,}) {
  return _then(_PrezziPiano(
mensile: null == mensile ? _self.mensile : mensile // ignore: cast_nullable_to_non_nullable
as PrezzoRinnovo,annuale: freezed == annuale ? _self.annuale : annuale // ignore: cast_nullable_to_non_nullable
as PrezzoRinnovo?,provaAnnuale: freezed == provaAnnuale ? _self.provaAnnuale : provaAnnuale // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}

/// Create a copy of PrezziPiano
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PrezzoRinnovoCopyWith<$Res> get mensile {
  
  return $PrezzoRinnovoCopyWith<$Res>(_self.mensile, (value) {
    return _then(_self.copyWith(mensile: value));
  });
}/// Create a copy of PrezziPiano
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PrezzoRinnovoCopyWith<$Res>? get annuale {
    if (_self.annuale == null) {
    return null;
  }

  return $PrezzoRinnovoCopyWith<$Res>(_self.annuale!, (value) {
    return _then(_self.copyWith(annuale: value));
  });
}
}


/// @nodoc
mixin _$Piano {

 String get slug; String get nome;/// `abbonamento` o `pacchetto`.
 String get tipo; String? get descrizione; String get valuta; int get prezzoMensile; int get prezzoAnnuale; int get creditiPerPeriodo; Map<String, num> get limiti; int? get livello; PrezziPiano? get prezzi;
/// Create a copy of Piano
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PianoCopyWith<Piano> get copyWith => _$PianoCopyWithImpl<Piano>(this as Piano, _$identity);

  /// Serializes this Piano to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Piano;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Piano&&(identical(other.slug, _this.slug) || other.slug == _this.slug)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.tipo, _this.tipo) || other.tipo == _this.tipo)&&(identical(other.descrizione, _this.descrizione) || other.descrizione == _this.descrizione)&&(identical(other.valuta, _this.valuta) || other.valuta == _this.valuta)&&(identical(other.prezzoMensile, _this.prezzoMensile) || other.prezzoMensile == _this.prezzoMensile)&&(identical(other.prezzoAnnuale, _this.prezzoAnnuale) || other.prezzoAnnuale == _this.prezzoAnnuale)&&(identical(other.creditiPerPeriodo, _this.creditiPerPeriodo) || other.creditiPerPeriodo == _this.creditiPerPeriodo)&&const DeepCollectionEquality().equals(other.limiti, _this.limiti)&&(identical(other.livello, _this.livello) || other.livello == _this.livello)&&(identical(other.prezzi, _this.prezzi) || other.prezzi == _this.prezzi));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Piano;
  return Object.hash(runtimeType,_this.slug,_this.nome,_this.tipo,_this.descrizione,_this.valuta,_this.prezzoMensile,_this.prezzoAnnuale,_this.creditiPerPeriodo,const DeepCollectionEquality().hash(_this.limiti),_this.livello,_this.prezzi);
}

@override
String toString() {
  final _this = this as Piano;
  return 'Piano(slug: ${_this.slug}, nome: ${_this.nome}, tipo: ${_this.tipo}, descrizione: ${_this.descrizione}, valuta: ${_this.valuta}, prezzoMensile: ${_this.prezzoMensile}, prezzoAnnuale: ${_this.prezzoAnnuale}, creditiPerPeriodo: ${_this.creditiPerPeriodo}, limiti: ${_this.limiti}, livello: ${_this.livello}, prezzi: ${_this.prezzi})';
}


}

/// @nodoc
abstract mixin class $PianoCopyWith<$Res>  {
  factory $PianoCopyWith(Piano value, $Res Function(Piano) _then) = _$PianoCopyWithImpl;
@useResult
$Res call({
 String slug, String nome, String tipo, String? descrizione, String valuta, int prezzoMensile, int prezzoAnnuale, int creditiPerPeriodo, Map<String, num> limiti, int? livello, PrezziPiano? prezzi
});


$PrezziPianoCopyWith<$Res>? get prezzi;

}
/// @nodoc
class _$PianoCopyWithImpl<$Res>
    implements $PianoCopyWith<$Res> {
  _$PianoCopyWithImpl(this._self, this._then);

  final Piano _self;
  final $Res Function(Piano) _then;

/// Create a copy of Piano
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? slug = null,Object? nome = null,Object? tipo = null,Object? descrizione = freezed,Object? valuta = null,Object? prezzoMensile = null,Object? prezzoAnnuale = null,Object? creditiPerPeriodo = null,Object? limiti = null,Object? livello = freezed,Object? prezzi = freezed,}) {
  return _then(Piano(
slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,descrizione: freezed == descrizione ? _self.descrizione : descrizione // ignore: cast_nullable_to_non_nullable
as String?,valuta: null == valuta ? _self.valuta : valuta // ignore: cast_nullable_to_non_nullable
as String,prezzoMensile: null == prezzoMensile ? _self.prezzoMensile : prezzoMensile // ignore: cast_nullable_to_non_nullable
as int,prezzoAnnuale: null == prezzoAnnuale ? _self.prezzoAnnuale : prezzoAnnuale // ignore: cast_nullable_to_non_nullable
as int,creditiPerPeriodo: null == creditiPerPeriodo ? _self.creditiPerPeriodo : creditiPerPeriodo // ignore: cast_nullable_to_non_nullable
as int,limiti: null == limiti ? _self.limiti : limiti // ignore: cast_nullable_to_non_nullable
as Map<String, num>,livello: freezed == livello ? _self.livello : livello // ignore: cast_nullable_to_non_nullable
as int?,prezzi: freezed == prezzi ? _self.prezzi : prezzi // ignore: cast_nullable_to_non_nullable
as PrezziPiano?,
  ));
}
/// Create a copy of Piano
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PrezziPianoCopyWith<$Res>? get prezzi {
    if (_self.prezzi == null) {
    return null;
  }

  return $PrezziPianoCopyWith<$Res>(_self.prezzi!, (value) {
    return _then(_self.copyWith(prezzi: value));
  });
}
}


/// Adds pattern-matching-related methods to [Piano].
extension PianoPatterns on Piano {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Piano value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Piano() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Piano value)  $default,){
final _that = this;
switch (_that) {
case _Piano():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Piano value)?  $default,){
final _that = this;
switch (_that) {
case _Piano() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String slug,  String nome,  String tipo,  String? descrizione,  String valuta,  int prezzoMensile,  int prezzoAnnuale,  int creditiPerPeriodo,  Map<String, num> limiti,  int? livello,  PrezziPiano? prezzi)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Piano() when $default != null:
return $default(_that.slug,_that.nome,_that.tipo,_that.descrizione,_that.valuta,_that.prezzoMensile,_that.prezzoAnnuale,_that.creditiPerPeriodo,_that.limiti,_that.livello,_that.prezzi);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String slug,  String nome,  String tipo,  String? descrizione,  String valuta,  int prezzoMensile,  int prezzoAnnuale,  int creditiPerPeriodo,  Map<String, num> limiti,  int? livello,  PrezziPiano? prezzi)  $default,) {final _that = this;
switch (_that) {
case _Piano():
return $default(_that.slug,_that.nome,_that.tipo,_that.descrizione,_that.valuta,_that.prezzoMensile,_that.prezzoAnnuale,_that.creditiPerPeriodo,_that.limiti,_that.livello,_that.prezzi);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String slug,  String nome,  String tipo,  String? descrizione,  String valuta,  int prezzoMensile,  int prezzoAnnuale,  int creditiPerPeriodo,  Map<String, num> limiti,  int? livello,  PrezziPiano? prezzi)?  $default,) {final _that = this;
switch (_that) {
case _Piano() when $default != null:
return $default(_that.slug,_that.nome,_that.tipo,_that.descrizione,_that.valuta,_that.prezzoMensile,_that.prezzoAnnuale,_that.creditiPerPeriodo,_that.limiti,_that.livello,_that.prezzi);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Piano extends Piano {
  const _Piano({required this.slug, required this.nome, required this.tipo, this.descrizione, this.valuta = 'EUR', this.prezzoMensile = 0, this.prezzoAnnuale = 0, this.creditiPerPeriodo = 0,  Map<String, num> limiti = const <String, num>{}, this.livello, this.prezzi}): _limiti = limiti,super._();
  factory _Piano.fromJson(Map<String, dynamic> json) => _$PianoFromJson(json);

@override final  String slug;
@override final  String nome;
/// `abbonamento` o `pacchetto`.
@override final  String tipo;
@override final  String? descrizione;
@override@JsonKey() final  String valuta;
@override@JsonKey() final  int prezzoMensile;
@override@JsonKey() final  int prezzoAnnuale;
@override@JsonKey() final  int creditiPerPeriodo;
 final  Map<String, num> _limiti;
@override@JsonKey() Map<String, num> get limiti {
  if (_limiti is EqualUnmodifiableMapView) return _limiti;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_limiti);
}

@override final  int? livello;
@override final  PrezziPiano? prezzi;

/// Create a copy of Piano
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PianoCopyWith<_Piano> get copyWith => __$PianoCopyWithImpl<_Piano>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PianoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Piano&&(identical(other.slug, slug) || other.slug == slug)&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.tipo, tipo) || other.tipo == tipo)&&(identical(other.descrizione, descrizione) || other.descrizione == descrizione)&&(identical(other.valuta, valuta) || other.valuta == valuta)&&(identical(other.prezzoMensile, prezzoMensile) || other.prezzoMensile == prezzoMensile)&&(identical(other.prezzoAnnuale, prezzoAnnuale) || other.prezzoAnnuale == prezzoAnnuale)&&(identical(other.creditiPerPeriodo, creditiPerPeriodo) || other.creditiPerPeriodo == creditiPerPeriodo)&&const DeepCollectionEquality().equals(other.limiti, _limiti)&&(identical(other.livello, livello) || other.livello == livello)&&(identical(other.prezzi, prezzi) || other.prezzi == prezzi));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,slug,nome,tipo,descrizione,valuta,prezzoMensile,prezzoAnnuale,creditiPerPeriodo,const DeepCollectionEquality().hash(_limiti),livello,prezzi);
}

@override
String toString() {
    return 'Piano(slug: $slug, nome: $nome, tipo: $tipo, descrizione: $descrizione, valuta: $valuta, prezzoMensile: $prezzoMensile, prezzoAnnuale: $prezzoAnnuale, creditiPerPeriodo: $creditiPerPeriodo, limiti: $limiti, livello: $livello, prezzi: $prezzi)';
}


}

/// @nodoc
abstract mixin class _$PianoCopyWith<$Res> implements $PianoCopyWith<$Res> {
  factory _$PianoCopyWith(_Piano value, $Res Function(_Piano) _then) = __$PianoCopyWithImpl;
@override @useResult
$Res call({
 String slug, String nome, String tipo, String? descrizione, String valuta, int prezzoMensile, int prezzoAnnuale, int creditiPerPeriodo, Map<String, num> limiti, int? livello, PrezziPiano? prezzi
});


@override $PrezziPianoCopyWith<$Res>? get prezzi;

}
/// @nodoc
class __$PianoCopyWithImpl<$Res>
    implements _$PianoCopyWith<$Res> {
  __$PianoCopyWithImpl(this._self, this._then);

  final _Piano _self;
  final $Res Function(_Piano) _then;

/// Create a copy of Piano
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? slug = null,Object? nome = null,Object? tipo = null,Object? descrizione = freezed,Object? valuta = null,Object? prezzoMensile = null,Object? prezzoAnnuale = null,Object? creditiPerPeriodo = null,Object? limiti = null,Object? livello = freezed,Object? prezzi = freezed,}) {
  return _then(_Piano(
slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,descrizione: freezed == descrizione ? _self.descrizione : descrizione // ignore: cast_nullable_to_non_nullable
as String?,valuta: null == valuta ? _self.valuta : valuta // ignore: cast_nullable_to_non_nullable
as String,prezzoMensile: null == prezzoMensile ? _self.prezzoMensile : prezzoMensile // ignore: cast_nullable_to_non_nullable
as int,prezzoAnnuale: null == prezzoAnnuale ? _self.prezzoAnnuale : prezzoAnnuale // ignore: cast_nullable_to_non_nullable
as int,creditiPerPeriodo: null == creditiPerPeriodo ? _self.creditiPerPeriodo : creditiPerPeriodo // ignore: cast_nullable_to_non_nullable
as int,limiti: null == limiti ? _self._limiti : limiti // ignore: cast_nullable_to_non_nullable
as Map<String, num>,livello: freezed == livello ? _self.livello : livello // ignore: cast_nullable_to_non_nullable
as int?,prezzi: freezed == prezzi ? _self.prezzi : prezzi // ignore: cast_nullable_to_non_nullable
as PrezziPiano?,
  ));
}

/// Create a copy of Piano
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PrezziPianoCopyWith<$Res>? get prezzi {
    if (_self.prezzi == null) {
    return null;
  }

  return $PrezziPianoCopyWith<$Res>(_self.prezzi!, (value) {
    return _then(_self.copyWith(prezzi: value));
  });
}
}


/// @nodoc
mixin _$AbbonamentoBreve {

 String get id; String get piano; String get nome; String get stato; String get periodoInizio; String get periodoFine; String? get disdettoIl; bool? get annuale; bool? get rinnovoAutomatico;/// Fase 9: chi incassa (`stripe`, `google_play`, `app_store`…) e se è un abbonamento di uno store.
 String? get provider; bool get store;
/// Create a copy of AbbonamentoBreve
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AbbonamentoBreveCopyWith<AbbonamentoBreve> get copyWith => _$AbbonamentoBreveCopyWithImpl<AbbonamentoBreve>(this as AbbonamentoBreve, _$identity);

  /// Serializes this AbbonamentoBreve to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as AbbonamentoBreve;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AbbonamentoBreve&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.piano, _this.piano) || other.piano == _this.piano)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.stato, _this.stato) || other.stato == _this.stato)&&(identical(other.periodoInizio, _this.periodoInizio) || other.periodoInizio == _this.periodoInizio)&&(identical(other.periodoFine, _this.periodoFine) || other.periodoFine == _this.periodoFine)&&(identical(other.disdettoIl, _this.disdettoIl) || other.disdettoIl == _this.disdettoIl)&&(identical(other.annuale, _this.annuale) || other.annuale == _this.annuale)&&(identical(other.rinnovoAutomatico, _this.rinnovoAutomatico) || other.rinnovoAutomatico == _this.rinnovoAutomatico)&&(identical(other.provider, _this.provider) || other.provider == _this.provider)&&(identical(other.store, _this.store) || other.store == _this.store));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as AbbonamentoBreve;
  return Object.hash(runtimeType,_this.id,_this.piano,_this.nome,_this.stato,_this.periodoInizio,_this.periodoFine,_this.disdettoIl,_this.annuale,_this.rinnovoAutomatico,_this.provider,_this.store);
}

@override
String toString() {
  final _this = this as AbbonamentoBreve;
  return 'AbbonamentoBreve(id: ${_this.id}, piano: ${_this.piano}, nome: ${_this.nome}, stato: ${_this.stato}, periodoInizio: ${_this.periodoInizio}, periodoFine: ${_this.periodoFine}, disdettoIl: ${_this.disdettoIl}, annuale: ${_this.annuale}, rinnovoAutomatico: ${_this.rinnovoAutomatico}, provider: ${_this.provider}, store: ${_this.store})';
}


}

/// @nodoc
abstract mixin class $AbbonamentoBreveCopyWith<$Res>  {
  factory $AbbonamentoBreveCopyWith(AbbonamentoBreve value, $Res Function(AbbonamentoBreve) _then) = _$AbbonamentoBreveCopyWithImpl;
@useResult
$Res call({
 String id, String piano, String nome, String stato, String periodoInizio, String periodoFine, String? disdettoIl, bool? annuale, bool? rinnovoAutomatico, String? provider, bool store
});




}
/// @nodoc
class _$AbbonamentoBreveCopyWithImpl<$Res>
    implements $AbbonamentoBreveCopyWith<$Res> {
  _$AbbonamentoBreveCopyWithImpl(this._self, this._then);

  final AbbonamentoBreve _self;
  final $Res Function(AbbonamentoBreve) _then;

/// Create a copy of AbbonamentoBreve
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? piano = null,Object? nome = null,Object? stato = null,Object? periodoInizio = null,Object? periodoFine = null,Object? disdettoIl = freezed,Object? annuale = freezed,Object? rinnovoAutomatico = freezed,Object? provider = freezed,Object? store = null,}) {
  return _then(AbbonamentoBreve(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,piano: null == piano ? _self.piano : piano // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,stato: null == stato ? _self.stato : stato // ignore: cast_nullable_to_non_nullable
as String,periodoInizio: null == periodoInizio ? _self.periodoInizio : periodoInizio // ignore: cast_nullable_to_non_nullable
as String,periodoFine: null == periodoFine ? _self.periodoFine : periodoFine // ignore: cast_nullable_to_non_nullable
as String,disdettoIl: freezed == disdettoIl ? _self.disdettoIl : disdettoIl // ignore: cast_nullable_to_non_nullable
as String?,annuale: freezed == annuale ? _self.annuale : annuale // ignore: cast_nullable_to_non_nullable
as bool?,rinnovoAutomatico: freezed == rinnovoAutomatico ? _self.rinnovoAutomatico : rinnovoAutomatico // ignore: cast_nullable_to_non_nullable
as bool?,provider: freezed == provider ? _self.provider : provider // ignore: cast_nullable_to_non_nullable
as String?,store: null == store ? _self.store : store // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [AbbonamentoBreve].
extension AbbonamentoBrevePatterns on AbbonamentoBreve {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _AbbonamentoBreve value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _AbbonamentoBreve() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _AbbonamentoBreve value)  $default,){
final _that = this;
switch (_that) {
case _AbbonamentoBreve():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _AbbonamentoBreve value)?  $default,){
final _that = this;
switch (_that) {
case _AbbonamentoBreve() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String piano,  String nome,  String stato,  String periodoInizio,  String periodoFine,  String? disdettoIl,  bool? annuale,  bool? rinnovoAutomatico,  String? provider,  bool store)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _AbbonamentoBreve() when $default != null:
return $default(_that.id,_that.piano,_that.nome,_that.stato,_that.periodoInizio,_that.periodoFine,_that.disdettoIl,_that.annuale,_that.rinnovoAutomatico,_that.provider,_that.store);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String piano,  String nome,  String stato,  String periodoInizio,  String periodoFine,  String? disdettoIl,  bool? annuale,  bool? rinnovoAutomatico,  String? provider,  bool store)  $default,) {final _that = this;
switch (_that) {
case _AbbonamentoBreve():
return $default(_that.id,_that.piano,_that.nome,_that.stato,_that.periodoInizio,_that.periodoFine,_that.disdettoIl,_that.annuale,_that.rinnovoAutomatico,_that.provider,_that.store);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String piano,  String nome,  String stato,  String periodoInizio,  String periodoFine,  String? disdettoIl,  bool? annuale,  bool? rinnovoAutomatico,  String? provider,  bool store)?  $default,) {final _that = this;
switch (_that) {
case _AbbonamentoBreve() when $default != null:
return $default(_that.id,_that.piano,_that.nome,_that.stato,_that.periodoInizio,_that.periodoFine,_that.disdettoIl,_that.annuale,_that.rinnovoAutomatico,_that.provider,_that.store);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _AbbonamentoBreve implements AbbonamentoBreve {
  const _AbbonamentoBreve({required this.id, required this.piano, required this.nome, required this.stato, required this.periodoInizio, required this.periodoFine, this.disdettoIl, this.annuale, this.rinnovoAutomatico, this.provider, this.store = false});
  factory _AbbonamentoBreve.fromJson(Map<String, dynamic> json) => _$AbbonamentoBreveFromJson(json);

@override final  String id;
@override final  String piano;
@override final  String nome;
@override final  String stato;
@override final  String periodoInizio;
@override final  String periodoFine;
@override final  String? disdettoIl;
@override final  bool? annuale;
@override final  bool? rinnovoAutomatico;
/// Fase 9: chi incassa (`stripe`, `google_play`, `app_store`…) e se è un abbonamento di uno store.
@override final  String? provider;
@override@JsonKey() final  bool store;

/// Create a copy of AbbonamentoBreve
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$AbbonamentoBreveCopyWith<_AbbonamentoBreve> get copyWith => __$AbbonamentoBreveCopyWithImpl<_AbbonamentoBreve>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$AbbonamentoBreveToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _AbbonamentoBreve&&(identical(other.id, id) || other.id == id)&&(identical(other.piano, piano) || other.piano == piano)&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.stato, stato) || other.stato == stato)&&(identical(other.periodoInizio, periodoInizio) || other.periodoInizio == periodoInizio)&&(identical(other.periodoFine, periodoFine) || other.periodoFine == periodoFine)&&(identical(other.disdettoIl, disdettoIl) || other.disdettoIl == disdettoIl)&&(identical(other.annuale, annuale) || other.annuale == annuale)&&(identical(other.rinnovoAutomatico, rinnovoAutomatico) || other.rinnovoAutomatico == rinnovoAutomatico)&&(identical(other.provider, provider) || other.provider == provider)&&(identical(other.store, store) || other.store == store));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,piano,nome,stato,periodoInizio,periodoFine,disdettoIl,annuale,rinnovoAutomatico,provider,store);
}

@override
String toString() {
    return 'AbbonamentoBreve(id: $id, piano: $piano, nome: $nome, stato: $stato, periodoInizio: $periodoInizio, periodoFine: $periodoFine, disdettoIl: $disdettoIl, annuale: $annuale, rinnovoAutomatico: $rinnovoAutomatico, provider: $provider, store: $store)';
}


}

/// @nodoc
abstract mixin class _$AbbonamentoBreveCopyWith<$Res> implements $AbbonamentoBreveCopyWith<$Res> {
  factory _$AbbonamentoBreveCopyWith(_AbbonamentoBreve value, $Res Function(_AbbonamentoBreve) _then) = __$AbbonamentoBreveCopyWithImpl;
@override @useResult
$Res call({
 String id, String piano, String nome, String stato, String periodoInizio, String periodoFine, String? disdettoIl, bool? annuale, bool? rinnovoAutomatico, String? provider, bool store
});




}
/// @nodoc
class __$AbbonamentoBreveCopyWithImpl<$Res>
    implements _$AbbonamentoBreveCopyWith<$Res> {
  __$AbbonamentoBreveCopyWithImpl(this._self, this._then);

  final _AbbonamentoBreve _self;
  final $Res Function(_AbbonamentoBreve) _then;

/// Create a copy of AbbonamentoBreve
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? piano = null,Object? nome = null,Object? stato = null,Object? periodoInizio = null,Object? periodoFine = null,Object? disdettoIl = freezed,Object? annuale = freezed,Object? rinnovoAutomatico = freezed,Object? provider = freezed,Object? store = null,}) {
  return _then(_AbbonamentoBreve(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,piano: null == piano ? _self.piano : piano // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,stato: null == stato ? _self.stato : stato // ignore: cast_nullable_to_non_nullable
as String,periodoInizio: null == periodoInizio ? _self.periodoInizio : periodoInizio // ignore: cast_nullable_to_non_nullable
as String,periodoFine: null == periodoFine ? _self.periodoFine : periodoFine // ignore: cast_nullable_to_non_nullable
as String,disdettoIl: freezed == disdettoIl ? _self.disdettoIl : disdettoIl // ignore: cast_nullable_to_non_nullable
as String?,annuale: freezed == annuale ? _self.annuale : annuale // ignore: cast_nullable_to_non_nullable
as bool?,rinnovoAutomatico: freezed == rinnovoAutomatico ? _self.rinnovoAutomatico : rinnovoAutomatico // ignore: cast_nullable_to_non_nullable
as bool?,provider: freezed == provider ? _self.provider : provider // ignore: cast_nullable_to_non_nullable
as String?,store: null == store ? _self.store : store // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}


/// @nodoc
mixin _$Diritti {

 String get piano; String get nome; Map<String, num> get limiti; bool get predefiniti;
/// Create a copy of Diritti
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DirittiCopyWith<Diritti> get copyWith => _$DirittiCopyWithImpl<Diritti>(this as Diritti, _$identity);

  /// Serializes this Diritti to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Diritti;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Diritti&&(identical(other.piano, _this.piano) || other.piano == _this.piano)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&const DeepCollectionEquality().equals(other.limiti, _this.limiti)&&(identical(other.predefiniti, _this.predefiniti) || other.predefiniti == _this.predefiniti));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Diritti;
  return Object.hash(runtimeType,_this.piano,_this.nome,const DeepCollectionEquality().hash(_this.limiti),_this.predefiniti);
}

@override
String toString() {
  final _this = this as Diritti;
  return 'Diritti(piano: ${_this.piano}, nome: ${_this.nome}, limiti: ${_this.limiti}, predefiniti: ${_this.predefiniti})';
}


}

/// @nodoc
abstract mixin class $DirittiCopyWith<$Res>  {
  factory $DirittiCopyWith(Diritti value, $Res Function(Diritti) _then) = _$DirittiCopyWithImpl;
@useResult
$Res call({
 String piano, String nome, Map<String, num> limiti, bool predefiniti
});




}
/// @nodoc
class _$DirittiCopyWithImpl<$Res>
    implements $DirittiCopyWith<$Res> {
  _$DirittiCopyWithImpl(this._self, this._then);

  final Diritti _self;
  final $Res Function(Diritti) _then;

/// Create a copy of Diritti
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? piano = null,Object? nome = null,Object? limiti = null,Object? predefiniti = null,}) {
  return _then(Diritti(
piano: null == piano ? _self.piano : piano // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,limiti: null == limiti ? _self.limiti : limiti // ignore: cast_nullable_to_non_nullable
as Map<String, num>,predefiniti: null == predefiniti ? _self.predefiniti : predefiniti // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [Diritti].
extension DirittiPatterns on Diritti {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Diritti value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Diritti() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Diritti value)  $default,){
final _that = this;
switch (_that) {
case _Diritti():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Diritti value)?  $default,){
final _that = this;
switch (_that) {
case _Diritti() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String piano,  String nome,  Map<String, num> limiti,  bool predefiniti)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Diritti() when $default != null:
return $default(_that.piano,_that.nome,_that.limiti,_that.predefiniti);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String piano,  String nome,  Map<String, num> limiti,  bool predefiniti)  $default,) {final _that = this;
switch (_that) {
case _Diritti():
return $default(_that.piano,_that.nome,_that.limiti,_that.predefiniti);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String piano,  String nome,  Map<String, num> limiti,  bool predefiniti)?  $default,) {final _that = this;
switch (_that) {
case _Diritti() when $default != null:
return $default(_that.piano,_that.nome,_that.limiti,_that.predefiniti);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Diritti implements Diritti {
  const _Diritti({required this.piano, required this.nome,  Map<String, num> limiti = const <String, num>{}, this.predefiniti = false}): _limiti = limiti;
  factory _Diritti.fromJson(Map<String, dynamic> json) => _$DirittiFromJson(json);

@override final  String piano;
@override final  String nome;
 final  Map<String, num> _limiti;
@override@JsonKey() Map<String, num> get limiti {
  if (_limiti is EqualUnmodifiableMapView) return _limiti;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_limiti);
}

@override@JsonKey() final  bool predefiniti;

/// Create a copy of Diritti
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DirittiCopyWith<_Diritti> get copyWith => __$DirittiCopyWithImpl<_Diritti>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$DirittiToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Diritti&&(identical(other.piano, piano) || other.piano == piano)&&(identical(other.nome, nome) || other.nome == nome)&&const DeepCollectionEquality().equals(other.limiti, _limiti)&&(identical(other.predefiniti, predefiniti) || other.predefiniti == predefiniti));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,piano,nome,const DeepCollectionEquality().hash(_limiti),predefiniti);
}

@override
String toString() {
    return 'Diritti(piano: $piano, nome: $nome, limiti: $limiti, predefiniti: $predefiniti)';
}


}

/// @nodoc
abstract mixin class _$DirittiCopyWith<$Res> implements $DirittiCopyWith<$Res> {
  factory _$DirittiCopyWith(_Diritti value, $Res Function(_Diritti) _then) = __$DirittiCopyWithImpl;
@override @useResult
$Res call({
 String piano, String nome, Map<String, num> limiti, bool predefiniti
});




}
/// @nodoc
class __$DirittiCopyWithImpl<$Res>
    implements _$DirittiCopyWith<$Res> {
  __$DirittiCopyWithImpl(this._self, this._then);

  final _Diritti _self;
  final $Res Function(_Diritti) _then;

/// Create a copy of Diritti
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? piano = null,Object? nome = null,Object? limiti = null,Object? predefiniti = null,}) {
  return _then(_Diritti(
piano: null == piano ? _self.piano : piano // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,limiti: null == limiti ? _self._limiti : limiti // ignore: cast_nullable_to_non_nullable
as Map<String, num>,predefiniti: null == predefiniti ? _self.predefiniti : predefiniti // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}


/// @nodoc
mixin _$UsoLimite {

 int get usati; int? get limite; int? get restanti;
/// Create a copy of UsoLimite
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UsoLimiteCopyWith<UsoLimite> get copyWith => _$UsoLimiteCopyWithImpl<UsoLimite>(this as UsoLimite, _$identity);

  /// Serializes this UsoLimite to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as UsoLimite;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UsoLimite&&(identical(other.usati, _this.usati) || other.usati == _this.usati)&&(identical(other.limite, _this.limite) || other.limite == _this.limite)&&(identical(other.restanti, _this.restanti) || other.restanti == _this.restanti));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as UsoLimite;
  return Object.hash(runtimeType,_this.usati,_this.limite,_this.restanti);
}

@override
String toString() {
  final _this = this as UsoLimite;
  return 'UsoLimite(usati: ${_this.usati}, limite: ${_this.limite}, restanti: ${_this.restanti})';
}


}

/// @nodoc
abstract mixin class $UsoLimiteCopyWith<$Res>  {
  factory $UsoLimiteCopyWith(UsoLimite value, $Res Function(UsoLimite) _then) = _$UsoLimiteCopyWithImpl;
@useResult
$Res call({
 int usati, int? limite, int? restanti
});




}
/// @nodoc
class _$UsoLimiteCopyWithImpl<$Res>
    implements $UsoLimiteCopyWith<$Res> {
  _$UsoLimiteCopyWithImpl(this._self, this._then);

  final UsoLimite _self;
  final $Res Function(UsoLimite) _then;

/// Create a copy of UsoLimite
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? usati = null,Object? limite = freezed,Object? restanti = freezed,}) {
  return _then(UsoLimite(
usati: null == usati ? _self.usati : usati // ignore: cast_nullable_to_non_nullable
as int,limite: freezed == limite ? _self.limite : limite // ignore: cast_nullable_to_non_nullable
as int?,restanti: freezed == restanti ? _self.restanti : restanti // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}

}


/// Adds pattern-matching-related methods to [UsoLimite].
extension UsoLimitePatterns on UsoLimite {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _UsoLimite value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _UsoLimite() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _UsoLimite value)  $default,){
final _that = this;
switch (_that) {
case _UsoLimite():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _UsoLimite value)?  $default,){
final _that = this;
switch (_that) {
case _UsoLimite() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int usati,  int? limite,  int? restanti)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _UsoLimite() when $default != null:
return $default(_that.usati,_that.limite,_that.restanti);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int usati,  int? limite,  int? restanti)  $default,) {final _that = this;
switch (_that) {
case _UsoLimite():
return $default(_that.usati,_that.limite,_that.restanti);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int usati,  int? limite,  int? restanti)?  $default,) {final _that = this;
switch (_that) {
case _UsoLimite() when $default != null:
return $default(_that.usati,_that.limite,_that.restanti);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _UsoLimite implements UsoLimite {
  const _UsoLimite({this.usati = 0, this.limite, this.restanti});
  factory _UsoLimite.fromJson(Map<String, dynamic> json) => _$UsoLimiteFromJson(json);

@override@JsonKey() final  int usati;
@override final  int? limite;
@override final  int? restanti;

/// Create a copy of UsoLimite
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UsoLimiteCopyWith<_UsoLimite> get copyWith => __$UsoLimiteCopyWithImpl<_UsoLimite>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$UsoLimiteToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _UsoLimite&&(identical(other.usati, usati) || other.usati == usati)&&(identical(other.limite, limite) || other.limite == limite)&&(identical(other.restanti, restanti) || other.restanti == restanti));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,usati,limite,restanti);
}

@override
String toString() {
    return 'UsoLimite(usati: $usati, limite: $limite, restanti: $restanti)';
}


}

/// @nodoc
abstract mixin class _$UsoLimiteCopyWith<$Res> implements $UsoLimiteCopyWith<$Res> {
  factory _$UsoLimiteCopyWith(_UsoLimite value, $Res Function(_UsoLimite) _then) = __$UsoLimiteCopyWithImpl;
@override @useResult
$Res call({
 int usati, int? limite, int? restanti
});




}
/// @nodoc
class __$UsoLimiteCopyWithImpl<$Res>
    implements _$UsoLimiteCopyWith<$Res> {
  __$UsoLimiteCopyWithImpl(this._self, this._then);

  final _UsoLimite _self;
  final $Res Function(_UsoLimite) _then;

/// Create a copy of UsoLimite
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? usati = null,Object? limite = freezed,Object? restanti = freezed,}) {
  return _then(_UsoLimite(
usati: null == usati ? _self.usati : usati // ignore: cast_nullable_to_non_nullable
as int,limite: freezed == limite ? _self.limite : limite // ignore: cast_nullable_to_non_nullable
as int?,restanti: freezed == restanti ? _self.restanti : restanti // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}


}


/// @nodoc
mixin _$IdoneitaProva {

 bool get idonea; String? get motivo; String? get usataIl;
/// Create a copy of IdoneitaProva
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$IdoneitaProvaCopyWith<IdoneitaProva> get copyWith => _$IdoneitaProvaCopyWithImpl<IdoneitaProva>(this as IdoneitaProva, _$identity);

  /// Serializes this IdoneitaProva to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as IdoneitaProva;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is IdoneitaProva&&(identical(other.idonea, _this.idonea) || other.idonea == _this.idonea)&&(identical(other.motivo, _this.motivo) || other.motivo == _this.motivo)&&(identical(other.usataIl, _this.usataIl) || other.usataIl == _this.usataIl));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as IdoneitaProva;
  return Object.hash(runtimeType,_this.idonea,_this.motivo,_this.usataIl);
}

@override
String toString() {
  final _this = this as IdoneitaProva;
  return 'IdoneitaProva(idonea: ${_this.idonea}, motivo: ${_this.motivo}, usataIl: ${_this.usataIl})';
}


}

/// @nodoc
abstract mixin class $IdoneitaProvaCopyWith<$Res>  {
  factory $IdoneitaProvaCopyWith(IdoneitaProva value, $Res Function(IdoneitaProva) _then) = _$IdoneitaProvaCopyWithImpl;
@useResult
$Res call({
 bool idonea, String? motivo, String? usataIl
});




}
/// @nodoc
class _$IdoneitaProvaCopyWithImpl<$Res>
    implements $IdoneitaProvaCopyWith<$Res> {
  _$IdoneitaProvaCopyWithImpl(this._self, this._then);

  final IdoneitaProva _self;
  final $Res Function(IdoneitaProva) _then;

/// Create a copy of IdoneitaProva
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? idonea = null,Object? motivo = freezed,Object? usataIl = freezed,}) {
  return _then(IdoneitaProva(
idonea: null == idonea ? _self.idonea : idonea // ignore: cast_nullable_to_non_nullable
as bool,motivo: freezed == motivo ? _self.motivo : motivo // ignore: cast_nullable_to_non_nullable
as String?,usataIl: freezed == usataIl ? _self.usataIl : usataIl // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [IdoneitaProva].
extension IdoneitaProvaPatterns on IdoneitaProva {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _IdoneitaProva value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _IdoneitaProva() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _IdoneitaProva value)  $default,){
final _that = this;
switch (_that) {
case _IdoneitaProva():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _IdoneitaProva value)?  $default,){
final _that = this;
switch (_that) {
case _IdoneitaProva() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( bool idonea,  String? motivo,  String? usataIl)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _IdoneitaProva() when $default != null:
return $default(_that.idonea,_that.motivo,_that.usataIl);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( bool idonea,  String? motivo,  String? usataIl)  $default,) {final _that = this;
switch (_that) {
case _IdoneitaProva():
return $default(_that.idonea,_that.motivo,_that.usataIl);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( bool idonea,  String? motivo,  String? usataIl)?  $default,) {final _that = this;
switch (_that) {
case _IdoneitaProva() when $default != null:
return $default(_that.idonea,_that.motivo,_that.usataIl);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _IdoneitaProva implements IdoneitaProva {
  const _IdoneitaProva({required this.idonea, this.motivo, this.usataIl});
  factory _IdoneitaProva.fromJson(Map<String, dynamic> json) => _$IdoneitaProvaFromJson(json);

@override final  bool idonea;
@override final  String? motivo;
@override final  String? usataIl;

/// Create a copy of IdoneitaProva
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$IdoneitaProvaCopyWith<_IdoneitaProva> get copyWith => __$IdoneitaProvaCopyWithImpl<_IdoneitaProva>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$IdoneitaProvaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _IdoneitaProva&&(identical(other.idonea, idonea) || other.idonea == idonea)&&(identical(other.motivo, motivo) || other.motivo == motivo)&&(identical(other.usataIl, usataIl) || other.usataIl == usataIl));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,idonea,motivo,usataIl);
}

@override
String toString() {
    return 'IdoneitaProva(idonea: $idonea, motivo: $motivo, usataIl: $usataIl)';
}


}

/// @nodoc
abstract mixin class _$IdoneitaProvaCopyWith<$Res> implements $IdoneitaProvaCopyWith<$Res> {
  factory _$IdoneitaProvaCopyWith(_IdoneitaProva value, $Res Function(_IdoneitaProva) _then) = __$IdoneitaProvaCopyWithImpl;
@override @useResult
$Res call({
 bool idonea, String? motivo, String? usataIl
});




}
/// @nodoc
class __$IdoneitaProvaCopyWithImpl<$Res>
    implements _$IdoneitaProvaCopyWith<$Res> {
  __$IdoneitaProvaCopyWithImpl(this._self, this._then);

  final _IdoneitaProva _self;
  final $Res Function(_IdoneitaProva) _then;

/// Create a copy of IdoneitaProva
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? idonea = null,Object? motivo = freezed,Object? usataIl = freezed,}) {
  return _then(_IdoneitaProva(
idonea: null == idonea ? _self.idonea : idonea // ignore: cast_nullable_to_non_nullable
as bool,motivo: freezed == motivo ? _self.motivo : motivo // ignore: cast_nullable_to_non_nullable
as String?,usataIl: freezed == usataIl ? _self.usataIl : usataIl // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$Conto {

 AbbonamentoBreve? get abbonamento; Diritti? get diritti; int get saldo; Map<String, UsoLimite> get uso; bool get limitiAttivi; bool? get lettureComprese; IdoneitaProva? get prova;
/// Create a copy of Conto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ContoCopyWith<Conto> get copyWith => _$ContoCopyWithImpl<Conto>(this as Conto, _$identity);

  /// Serializes this Conto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Conto;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Conto&&(identical(other.abbonamento, _this.abbonamento) || other.abbonamento == _this.abbonamento)&&(identical(other.diritti, _this.diritti) || other.diritti == _this.diritti)&&(identical(other.saldo, _this.saldo) || other.saldo == _this.saldo)&&const DeepCollectionEquality().equals(other.uso, _this.uso)&&(identical(other.limitiAttivi, _this.limitiAttivi) || other.limitiAttivi == _this.limitiAttivi)&&(identical(other.lettureComprese, _this.lettureComprese) || other.lettureComprese == _this.lettureComprese)&&(identical(other.prova, _this.prova) || other.prova == _this.prova));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Conto;
  return Object.hash(runtimeType,_this.abbonamento,_this.diritti,_this.saldo,const DeepCollectionEquality().hash(_this.uso),_this.limitiAttivi,_this.lettureComprese,_this.prova);
}

@override
String toString() {
  final _this = this as Conto;
  return 'Conto(abbonamento: ${_this.abbonamento}, diritti: ${_this.diritti}, saldo: ${_this.saldo}, uso: ${_this.uso}, limitiAttivi: ${_this.limitiAttivi}, lettureComprese: ${_this.lettureComprese}, prova: ${_this.prova})';
}


}

/// @nodoc
abstract mixin class $ContoCopyWith<$Res>  {
  factory $ContoCopyWith(Conto value, $Res Function(Conto) _then) = _$ContoCopyWithImpl;
@useResult
$Res call({
 AbbonamentoBreve? abbonamento, Diritti? diritti, int saldo, Map<String, UsoLimite> uso, bool limitiAttivi, bool? lettureComprese, IdoneitaProva? prova
});


$AbbonamentoBreveCopyWith<$Res>? get abbonamento;$DirittiCopyWith<$Res>? get diritti;$IdoneitaProvaCopyWith<$Res>? get prova;

}
/// @nodoc
class _$ContoCopyWithImpl<$Res>
    implements $ContoCopyWith<$Res> {
  _$ContoCopyWithImpl(this._self, this._then);

  final Conto _self;
  final $Res Function(Conto) _then;

/// Create a copy of Conto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? abbonamento = freezed,Object? diritti = freezed,Object? saldo = null,Object? uso = null,Object? limitiAttivi = null,Object? lettureComprese = freezed,Object? prova = freezed,}) {
  return _then(Conto(
abbonamento: freezed == abbonamento ? _self.abbonamento : abbonamento // ignore: cast_nullable_to_non_nullable
as AbbonamentoBreve?,diritti: freezed == diritti ? _self.diritti : diritti // ignore: cast_nullable_to_non_nullable
as Diritti?,saldo: null == saldo ? _self.saldo : saldo // ignore: cast_nullable_to_non_nullable
as int,uso: null == uso ? _self.uso : uso // ignore: cast_nullable_to_non_nullable
as Map<String, UsoLimite>,limitiAttivi: null == limitiAttivi ? _self.limitiAttivi : limitiAttivi // ignore: cast_nullable_to_non_nullable
as bool,lettureComprese: freezed == lettureComprese ? _self.lettureComprese : lettureComprese // ignore: cast_nullable_to_non_nullable
as bool?,prova: freezed == prova ? _self.prova : prova // ignore: cast_nullable_to_non_nullable
as IdoneitaProva?,
  ));
}
/// Create a copy of Conto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$AbbonamentoBreveCopyWith<$Res>? get abbonamento {
    if (_self.abbonamento == null) {
    return null;
  }

  return $AbbonamentoBreveCopyWith<$Res>(_self.abbonamento!, (value) {
    return _then(_self.copyWith(abbonamento: value));
  });
}/// Create a copy of Conto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$DirittiCopyWith<$Res>? get diritti {
    if (_self.diritti == null) {
    return null;
  }

  return $DirittiCopyWith<$Res>(_self.diritti!, (value) {
    return _then(_self.copyWith(diritti: value));
  });
}/// Create a copy of Conto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$IdoneitaProvaCopyWith<$Res>? get prova {
    if (_self.prova == null) {
    return null;
  }

  return $IdoneitaProvaCopyWith<$Res>(_self.prova!, (value) {
    return _then(_self.copyWith(prova: value));
  });
}
}


/// Adds pattern-matching-related methods to [Conto].
extension ContoPatterns on Conto {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Conto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Conto() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Conto value)  $default,){
final _that = this;
switch (_that) {
case _Conto():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Conto value)?  $default,){
final _that = this;
switch (_that) {
case _Conto() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( AbbonamentoBreve? abbonamento,  Diritti? diritti,  int saldo,  Map<String, UsoLimite> uso,  bool limitiAttivi,  bool? lettureComprese,  IdoneitaProva? prova)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Conto() when $default != null:
return $default(_that.abbonamento,_that.diritti,_that.saldo,_that.uso,_that.limitiAttivi,_that.lettureComprese,_that.prova);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( AbbonamentoBreve? abbonamento,  Diritti? diritti,  int saldo,  Map<String, UsoLimite> uso,  bool limitiAttivi,  bool? lettureComprese,  IdoneitaProva? prova)  $default,) {final _that = this;
switch (_that) {
case _Conto():
return $default(_that.abbonamento,_that.diritti,_that.saldo,_that.uso,_that.limitiAttivi,_that.lettureComprese,_that.prova);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( AbbonamentoBreve? abbonamento,  Diritti? diritti,  int saldo,  Map<String, UsoLimite> uso,  bool limitiAttivi,  bool? lettureComprese,  IdoneitaProva? prova)?  $default,) {final _that = this;
switch (_that) {
case _Conto() when $default != null:
return $default(_that.abbonamento,_that.diritti,_that.saldo,_that.uso,_that.limitiAttivi,_that.lettureComprese,_that.prova);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Conto implements Conto {
  const _Conto({this.abbonamento, this.diritti, this.saldo = 0,  Map<String, UsoLimite> uso = const <String, UsoLimite>{}, this.limitiAttivi = false, this.lettureComprese, this.prova}): _uso = uso;
  factory _Conto.fromJson(Map<String, dynamic> json) => _$ContoFromJson(json);

@override final  AbbonamentoBreve? abbonamento;
@override final  Diritti? diritti;
@override@JsonKey() final  int saldo;
 final  Map<String, UsoLimite> _uso;
@override@JsonKey() Map<String, UsoLimite> get uso {
  if (_uso is EqualUnmodifiableMapView) return _uso;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_uso);
}

@override@JsonKey() final  bool limitiAttivi;
@override final  bool? lettureComprese;
@override final  IdoneitaProva? prova;

/// Create a copy of Conto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ContoCopyWith<_Conto> get copyWith => __$ContoCopyWithImpl<_Conto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ContoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Conto&&(identical(other.abbonamento, abbonamento) || other.abbonamento == abbonamento)&&(identical(other.diritti, diritti) || other.diritti == diritti)&&(identical(other.saldo, saldo) || other.saldo == saldo)&&const DeepCollectionEquality().equals(other.uso, _uso)&&(identical(other.limitiAttivi, limitiAttivi) || other.limitiAttivi == limitiAttivi)&&(identical(other.lettureComprese, lettureComprese) || other.lettureComprese == lettureComprese)&&(identical(other.prova, prova) || other.prova == prova));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,abbonamento,diritti,saldo,const DeepCollectionEquality().hash(_uso),limitiAttivi,lettureComprese,prova);
}

@override
String toString() {
    return 'Conto(abbonamento: $abbonamento, diritti: $diritti, saldo: $saldo, uso: $uso, limitiAttivi: $limitiAttivi, lettureComprese: $lettureComprese, prova: $prova)';
}


}

/// @nodoc
abstract mixin class _$ContoCopyWith<$Res> implements $ContoCopyWith<$Res> {
  factory _$ContoCopyWith(_Conto value, $Res Function(_Conto) _then) = __$ContoCopyWithImpl;
@override @useResult
$Res call({
 AbbonamentoBreve? abbonamento, Diritti? diritti, int saldo, Map<String, UsoLimite> uso, bool limitiAttivi, bool? lettureComprese, IdoneitaProva? prova
});


@override $AbbonamentoBreveCopyWith<$Res>? get abbonamento;@override $DirittiCopyWith<$Res>? get diritti;@override $IdoneitaProvaCopyWith<$Res>? get prova;

}
/// @nodoc
class __$ContoCopyWithImpl<$Res>
    implements _$ContoCopyWith<$Res> {
  __$ContoCopyWithImpl(this._self, this._then);

  final _Conto _self;
  final $Res Function(_Conto) _then;

/// Create a copy of Conto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? abbonamento = freezed,Object? diritti = freezed,Object? saldo = null,Object? uso = null,Object? limitiAttivi = null,Object? lettureComprese = freezed,Object? prova = freezed,}) {
  return _then(_Conto(
abbonamento: freezed == abbonamento ? _self.abbonamento : abbonamento // ignore: cast_nullable_to_non_nullable
as AbbonamentoBreve?,diritti: freezed == diritti ? _self.diritti : diritti // ignore: cast_nullable_to_non_nullable
as Diritti?,saldo: null == saldo ? _self.saldo : saldo // ignore: cast_nullable_to_non_nullable
as int,uso: null == uso ? _self._uso : uso // ignore: cast_nullable_to_non_nullable
as Map<String, UsoLimite>,limitiAttivi: null == limitiAttivi ? _self.limitiAttivi : limitiAttivi // ignore: cast_nullable_to_non_nullable
as bool,lettureComprese: freezed == lettureComprese ? _self.lettureComprese : lettureComprese // ignore: cast_nullable_to_non_nullable
as bool?,prova: freezed == prova ? _self.prova : prova // ignore: cast_nullable_to_non_nullable
as IdoneitaProva?,
  ));
}

/// Create a copy of Conto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$AbbonamentoBreveCopyWith<$Res>? get abbonamento {
    if (_self.abbonamento == null) {
    return null;
  }

  return $AbbonamentoBreveCopyWith<$Res>(_self.abbonamento!, (value) {
    return _then(_self.copyWith(abbonamento: value));
  });
}/// Create a copy of Conto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$DirittiCopyWith<$Res>? get diritti {
    if (_self.diritti == null) {
    return null;
  }

  return $DirittiCopyWith<$Res>(_self.diritti!, (value) {
    return _then(_self.copyWith(diritti: value));
  });
}/// Create a copy of Conto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$IdoneitaProvaCopyWith<$Res>? get prova {
    if (_self.prova == null) {
    return null;
  }

  return $IdoneitaProvaCopyWith<$Res>(_self.prova!, (value) {
    return _then(_self.copyWith(prova: value));
  });
}
}


/// @nodoc
mixin _$Movimento {

 int get delta; String get reason; String get quando; String? get note; String? get readingId;
/// Create a copy of Movimento
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MovimentoCopyWith<Movimento> get copyWith => _$MovimentoCopyWithImpl<Movimento>(this as Movimento, _$identity);

  /// Serializes this Movimento to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Movimento;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Movimento&&(identical(other.delta, _this.delta) || other.delta == _this.delta)&&(identical(other.reason, _this.reason) || other.reason == _this.reason)&&(identical(other.quando, _this.quando) || other.quando == _this.quando)&&(identical(other.note, _this.note) || other.note == _this.note)&&(identical(other.readingId, _this.readingId) || other.readingId == _this.readingId));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Movimento;
  return Object.hash(runtimeType,_this.delta,_this.reason,_this.quando,_this.note,_this.readingId);
}

@override
String toString() {
  final _this = this as Movimento;
  return 'Movimento(delta: ${_this.delta}, reason: ${_this.reason}, quando: ${_this.quando}, note: ${_this.note}, readingId: ${_this.readingId})';
}


}

/// @nodoc
abstract mixin class $MovimentoCopyWith<$Res>  {
  factory $MovimentoCopyWith(Movimento value, $Res Function(Movimento) _then) = _$MovimentoCopyWithImpl;
@useResult
$Res call({
 int delta, String reason, String quando, String? note, String? readingId
});




}
/// @nodoc
class _$MovimentoCopyWithImpl<$Res>
    implements $MovimentoCopyWith<$Res> {
  _$MovimentoCopyWithImpl(this._self, this._then);

  final Movimento _self;
  final $Res Function(Movimento) _then;

/// Create a copy of Movimento
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? delta = null,Object? reason = null,Object? quando = null,Object? note = freezed,Object? readingId = freezed,}) {
  return _then(Movimento(
delta: null == delta ? _self.delta : delta // ignore: cast_nullable_to_non_nullable
as int,reason: null == reason ? _self.reason : reason // ignore: cast_nullable_to_non_nullable
as String,quando: null == quando ? _self.quando : quando // ignore: cast_nullable_to_non_nullable
as String,note: freezed == note ? _self.note : note // ignore: cast_nullable_to_non_nullable
as String?,readingId: freezed == readingId ? _self.readingId : readingId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [Movimento].
extension MovimentoPatterns on Movimento {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Movimento value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Movimento() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Movimento value)  $default,){
final _that = this;
switch (_that) {
case _Movimento():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Movimento value)?  $default,){
final _that = this;
switch (_that) {
case _Movimento() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int delta,  String reason,  String quando,  String? note,  String? readingId)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Movimento() when $default != null:
return $default(_that.delta,_that.reason,_that.quando,_that.note,_that.readingId);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int delta,  String reason,  String quando,  String? note,  String? readingId)  $default,) {final _that = this;
switch (_that) {
case _Movimento():
return $default(_that.delta,_that.reason,_that.quando,_that.note,_that.readingId);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int delta,  String reason,  String quando,  String? note,  String? readingId)?  $default,) {final _that = this;
switch (_that) {
case _Movimento() when $default != null:
return $default(_that.delta,_that.reason,_that.quando,_that.note,_that.readingId);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Movimento implements Movimento {
  const _Movimento({required this.delta, required this.reason, required this.quando, this.note, this.readingId});
  factory _Movimento.fromJson(Map<String, dynamic> json) => _$MovimentoFromJson(json);

@override final  int delta;
@override final  String reason;
@override final  String quando;
@override final  String? note;
@override final  String? readingId;

/// Create a copy of Movimento
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MovimentoCopyWith<_Movimento> get copyWith => __$MovimentoCopyWithImpl<_Movimento>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MovimentoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Movimento&&(identical(other.delta, delta) || other.delta == delta)&&(identical(other.reason, reason) || other.reason == reason)&&(identical(other.quando, quando) || other.quando == quando)&&(identical(other.note, note) || other.note == note)&&(identical(other.readingId, readingId) || other.readingId == readingId));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,delta,reason,quando,note,readingId);
}

@override
String toString() {
    return 'Movimento(delta: $delta, reason: $reason, quando: $quando, note: $note, readingId: $readingId)';
}


}

/// @nodoc
abstract mixin class _$MovimentoCopyWith<$Res> implements $MovimentoCopyWith<$Res> {
  factory _$MovimentoCopyWith(_Movimento value, $Res Function(_Movimento) _then) = __$MovimentoCopyWithImpl;
@override @useResult
$Res call({
 int delta, String reason, String quando, String? note, String? readingId
});




}
/// @nodoc
class __$MovimentoCopyWithImpl<$Res>
    implements _$MovimentoCopyWith<$Res> {
  __$MovimentoCopyWithImpl(this._self, this._then);

  final _Movimento _self;
  final $Res Function(_Movimento) _then;

/// Create a copy of Movimento
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? delta = null,Object? reason = null,Object? quando = null,Object? note = freezed,Object? readingId = freezed,}) {
  return _then(_Movimento(
delta: null == delta ? _self.delta : delta // ignore: cast_nullable_to_non_nullable
as int,reason: null == reason ? _self.reason : reason // ignore: cast_nullable_to_non_nullable
as String,quando: null == quando ? _self.quando : quando // ignore: cast_nullable_to_non_nullable
as String,note: freezed == note ? _self.note : note // ignore: cast_nullable_to_non_nullable
as String?,readingId: freezed == readingId ? _self.readingId : readingId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$Movimenti {

 int get saldo; List<Movimento> get movimenti;
/// Create a copy of Movimenti
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MovimentiCopyWith<Movimenti> get copyWith => _$MovimentiCopyWithImpl<Movimenti>(this as Movimenti, _$identity);

  /// Serializes this Movimenti to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Movimenti;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Movimenti&&(identical(other.saldo, _this.saldo) || other.saldo == _this.saldo)&&const DeepCollectionEquality().equals(other.movimenti, _this.movimenti));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Movimenti;
  return Object.hash(runtimeType,_this.saldo,const DeepCollectionEquality().hash(_this.movimenti));
}

@override
String toString() {
  final _this = this as Movimenti;
  return 'Movimenti(saldo: ${_this.saldo}, movimenti: ${_this.movimenti})';
}


}

/// @nodoc
abstract mixin class $MovimentiCopyWith<$Res>  {
  factory $MovimentiCopyWith(Movimenti value, $Res Function(Movimenti) _then) = _$MovimentiCopyWithImpl;
@useResult
$Res call({
 int saldo, List<Movimento> movimenti
});




}
/// @nodoc
class _$MovimentiCopyWithImpl<$Res>
    implements $MovimentiCopyWith<$Res> {
  _$MovimentiCopyWithImpl(this._self, this._then);

  final Movimenti _self;
  final $Res Function(Movimenti) _then;

/// Create a copy of Movimenti
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? saldo = null,Object? movimenti = null,}) {
  return _then(Movimenti(
saldo: null == saldo ? _self.saldo : saldo // ignore: cast_nullable_to_non_nullable
as int,movimenti: null == movimenti ? _self.movimenti : movimenti // ignore: cast_nullable_to_non_nullable
as List<Movimento>,
  ));
}

}


/// Adds pattern-matching-related methods to [Movimenti].
extension MovimentiPatterns on Movimenti {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Movimenti value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Movimenti() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Movimenti value)  $default,){
final _that = this;
switch (_that) {
case _Movimenti():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Movimenti value)?  $default,){
final _that = this;
switch (_that) {
case _Movimenti() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int saldo,  List<Movimento> movimenti)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Movimenti() when $default != null:
return $default(_that.saldo,_that.movimenti);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int saldo,  List<Movimento> movimenti)  $default,) {final _that = this;
switch (_that) {
case _Movimenti():
return $default(_that.saldo,_that.movimenti);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int saldo,  List<Movimento> movimenti)?  $default,) {final _that = this;
switch (_that) {
case _Movimenti() when $default != null:
return $default(_that.saldo,_that.movimenti);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Movimenti implements Movimenti {
  const _Movimenti({this.saldo = 0,  List<Movimento> movimenti = const <Movimento>[]}): _movimenti = movimenti;
  factory _Movimenti.fromJson(Map<String, dynamic> json) => _$MovimentiFromJson(json);

@override@JsonKey() final  int saldo;
 final  List<Movimento> _movimenti;
@override@JsonKey() List<Movimento> get movimenti {
  if (_movimenti is EqualUnmodifiableListView) return _movimenti;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_movimenti);
}


/// Create a copy of Movimenti
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MovimentiCopyWith<_Movimenti> get copyWith => __$MovimentiCopyWithImpl<_Movimenti>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MovimentiToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Movimenti&&(identical(other.saldo, saldo) || other.saldo == saldo)&&const DeepCollectionEquality().equals(other.movimenti, _movimenti));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,saldo,const DeepCollectionEquality().hash(_movimenti));
}

@override
String toString() {
    return 'Movimenti(saldo: $saldo, movimenti: $movimenti)';
}


}

/// @nodoc
abstract mixin class _$MovimentiCopyWith<$Res> implements $MovimentiCopyWith<$Res> {
  factory _$MovimentiCopyWith(_Movimenti value, $Res Function(_Movimenti) _then) = __$MovimentiCopyWithImpl;
@override @useResult
$Res call({
 int saldo, List<Movimento> movimenti
});




}
/// @nodoc
class __$MovimentiCopyWithImpl<$Res>
    implements _$MovimentiCopyWith<$Res> {
  __$MovimentiCopyWithImpl(this._self, this._then);

  final _Movimenti _self;
  final $Res Function(_Movimenti) _then;

/// Create a copy of Movimenti
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? saldo = null,Object? movimenti = null,}) {
  return _then(_Movimenti(
saldo: null == saldo ? _self.saldo : saldo // ignore: cast_nullable_to_non_nullable
as int,movimenti: null == movimenti ? _self._movimenti : movimenti // ignore: cast_nullable_to_non_nullable
as List<Movimento>,
  ));
}


}


/// @nodoc
mixin _$Checkout {

 String get checkoutId; String get url; int get importo; int? get sconto; String get valuta; bool get gratis;
/// Create a copy of Checkout
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CheckoutCopyWith<Checkout> get copyWith => _$CheckoutCopyWithImpl<Checkout>(this as Checkout, _$identity);

  /// Serializes this Checkout to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Checkout;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Checkout&&(identical(other.checkoutId, _this.checkoutId) || other.checkoutId == _this.checkoutId)&&(identical(other.url, _this.url) || other.url == _this.url)&&(identical(other.importo, _this.importo) || other.importo == _this.importo)&&(identical(other.sconto, _this.sconto) || other.sconto == _this.sconto)&&(identical(other.valuta, _this.valuta) || other.valuta == _this.valuta)&&(identical(other.gratis, _this.gratis) || other.gratis == _this.gratis));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Checkout;
  return Object.hash(runtimeType,_this.checkoutId,_this.url,_this.importo,_this.sconto,_this.valuta,_this.gratis);
}

@override
String toString() {
  final _this = this as Checkout;
  return 'Checkout(checkoutId: ${_this.checkoutId}, url: ${_this.url}, importo: ${_this.importo}, sconto: ${_this.sconto}, valuta: ${_this.valuta}, gratis: ${_this.gratis})';
}


}

/// @nodoc
abstract mixin class $CheckoutCopyWith<$Res>  {
  factory $CheckoutCopyWith(Checkout value, $Res Function(Checkout) _then) = _$CheckoutCopyWithImpl;
@useResult
$Res call({
 String checkoutId, String url, int importo, int? sconto, String valuta, bool gratis
});




}
/// @nodoc
class _$CheckoutCopyWithImpl<$Res>
    implements $CheckoutCopyWith<$Res> {
  _$CheckoutCopyWithImpl(this._self, this._then);

  final Checkout _self;
  final $Res Function(Checkout) _then;

/// Create a copy of Checkout
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? checkoutId = null,Object? url = null,Object? importo = null,Object? sconto = freezed,Object? valuta = null,Object? gratis = null,}) {
  return _then(Checkout(
checkoutId: null == checkoutId ? _self.checkoutId : checkoutId // ignore: cast_nullable_to_non_nullable
as String,url: null == url ? _self.url : url // ignore: cast_nullable_to_non_nullable
as String,importo: null == importo ? _self.importo : importo // ignore: cast_nullable_to_non_nullable
as int,sconto: freezed == sconto ? _self.sconto : sconto // ignore: cast_nullable_to_non_nullable
as int?,valuta: null == valuta ? _self.valuta : valuta // ignore: cast_nullable_to_non_nullable
as String,gratis: null == gratis ? _self.gratis : gratis // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [Checkout].
extension CheckoutPatterns on Checkout {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Checkout value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Checkout() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Checkout value)  $default,){
final _that = this;
switch (_that) {
case _Checkout():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Checkout value)?  $default,){
final _that = this;
switch (_that) {
case _Checkout() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String checkoutId,  String url,  int importo,  int? sconto,  String valuta,  bool gratis)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Checkout() when $default != null:
return $default(_that.checkoutId,_that.url,_that.importo,_that.sconto,_that.valuta,_that.gratis);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String checkoutId,  String url,  int importo,  int? sconto,  String valuta,  bool gratis)  $default,) {final _that = this;
switch (_that) {
case _Checkout():
return $default(_that.checkoutId,_that.url,_that.importo,_that.sconto,_that.valuta,_that.gratis);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String checkoutId,  String url,  int importo,  int? sconto,  String valuta,  bool gratis)?  $default,) {final _that = this;
switch (_that) {
case _Checkout() when $default != null:
return $default(_that.checkoutId,_that.url,_that.importo,_that.sconto,_that.valuta,_that.gratis);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Checkout implements Checkout {
  const _Checkout({required this.checkoutId, required this.url, this.importo = 0, this.sconto, this.valuta = 'EUR', this.gratis = false});
  factory _Checkout.fromJson(Map<String, dynamic> json) => _$CheckoutFromJson(json);

@override final  String checkoutId;
@override final  String url;
@override@JsonKey() final  int importo;
@override final  int? sconto;
@override@JsonKey() final  String valuta;
@override@JsonKey() final  bool gratis;

/// Create a copy of Checkout
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CheckoutCopyWith<_Checkout> get copyWith => __$CheckoutCopyWithImpl<_Checkout>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CheckoutToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Checkout&&(identical(other.checkoutId, checkoutId) || other.checkoutId == checkoutId)&&(identical(other.url, url) || other.url == url)&&(identical(other.importo, importo) || other.importo == importo)&&(identical(other.sconto, sconto) || other.sconto == sconto)&&(identical(other.valuta, valuta) || other.valuta == valuta)&&(identical(other.gratis, gratis) || other.gratis == gratis));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,checkoutId,url,importo,sconto,valuta,gratis);
}

@override
String toString() {
    return 'Checkout(checkoutId: $checkoutId, url: $url, importo: $importo, sconto: $sconto, valuta: $valuta, gratis: $gratis)';
}


}

/// @nodoc
abstract mixin class _$CheckoutCopyWith<$Res> implements $CheckoutCopyWith<$Res> {
  factory _$CheckoutCopyWith(_Checkout value, $Res Function(_Checkout) _then) = __$CheckoutCopyWithImpl;
@override @useResult
$Res call({
 String checkoutId, String url, int importo, int? sconto, String valuta, bool gratis
});




}
/// @nodoc
class __$CheckoutCopyWithImpl<$Res>
    implements _$CheckoutCopyWith<$Res> {
  __$CheckoutCopyWithImpl(this._self, this._then);

  final _Checkout _self;
  final $Res Function(_Checkout) _then;

/// Create a copy of Checkout
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? checkoutId = null,Object? url = null,Object? importo = null,Object? sconto = freezed,Object? valuta = null,Object? gratis = null,}) {
  return _then(_Checkout(
checkoutId: null == checkoutId ? _self.checkoutId : checkoutId // ignore: cast_nullable_to_non_nullable
as String,url: null == url ? _self.url : url // ignore: cast_nullable_to_non_nullable
as String,importo: null == importo ? _self.importo : importo // ignore: cast_nullable_to_non_nullable
as int,sconto: freezed == sconto ? _self.sconto : sconto // ignore: cast_nullable_to_non_nullable
as int?,valuta: null == valuta ? _self.valuta : valuta // ignore: cast_nullable_to_non_nullable
as String,gratis: null == gratis ? _self.gratis : gratis // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}


/// @nodoc
mixin _$StatoCheckout {

 String get checkoutId; String get stato; String get piano; String get nome; String get tipo; bool? get prova; bool? get cambio; String? get esito;
/// Create a copy of StatoCheckout
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$StatoCheckoutCopyWith<StatoCheckout> get copyWith => _$StatoCheckoutCopyWithImpl<StatoCheckout>(this as StatoCheckout, _$identity);

  /// Serializes this StatoCheckout to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as StatoCheckout;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is StatoCheckout&&(identical(other.checkoutId, _this.checkoutId) || other.checkoutId == _this.checkoutId)&&(identical(other.stato, _this.stato) || other.stato == _this.stato)&&(identical(other.piano, _this.piano) || other.piano == _this.piano)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.tipo, _this.tipo) || other.tipo == _this.tipo)&&(identical(other.prova, _this.prova) || other.prova == _this.prova)&&(identical(other.cambio, _this.cambio) || other.cambio == _this.cambio)&&(identical(other.esito, _this.esito) || other.esito == _this.esito));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as StatoCheckout;
  return Object.hash(runtimeType,_this.checkoutId,_this.stato,_this.piano,_this.nome,_this.tipo,_this.prova,_this.cambio,_this.esito);
}

@override
String toString() {
  final _this = this as StatoCheckout;
  return 'StatoCheckout(checkoutId: ${_this.checkoutId}, stato: ${_this.stato}, piano: ${_this.piano}, nome: ${_this.nome}, tipo: ${_this.tipo}, prova: ${_this.prova}, cambio: ${_this.cambio}, esito: ${_this.esito})';
}


}

/// @nodoc
abstract mixin class $StatoCheckoutCopyWith<$Res>  {
  factory $StatoCheckoutCopyWith(StatoCheckout value, $Res Function(StatoCheckout) _then) = _$StatoCheckoutCopyWithImpl;
@useResult
$Res call({
 String checkoutId, String stato, String piano, String nome, String tipo, bool? prova, bool? cambio, String? esito
});




}
/// @nodoc
class _$StatoCheckoutCopyWithImpl<$Res>
    implements $StatoCheckoutCopyWith<$Res> {
  _$StatoCheckoutCopyWithImpl(this._self, this._then);

  final StatoCheckout _self;
  final $Res Function(StatoCheckout) _then;

/// Create a copy of StatoCheckout
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? checkoutId = null,Object? stato = null,Object? piano = null,Object? nome = null,Object? tipo = null,Object? prova = freezed,Object? cambio = freezed,Object? esito = freezed,}) {
  return _then(StatoCheckout(
checkoutId: null == checkoutId ? _self.checkoutId : checkoutId // ignore: cast_nullable_to_non_nullable
as String,stato: null == stato ? _self.stato : stato // ignore: cast_nullable_to_non_nullable
as String,piano: null == piano ? _self.piano : piano // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,prova: freezed == prova ? _self.prova : prova // ignore: cast_nullable_to_non_nullable
as bool?,cambio: freezed == cambio ? _self.cambio : cambio // ignore: cast_nullable_to_non_nullable
as bool?,esito: freezed == esito ? _self.esito : esito // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [StatoCheckout].
extension StatoCheckoutPatterns on StatoCheckout {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _StatoCheckout value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _StatoCheckout() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _StatoCheckout value)  $default,){
final _that = this;
switch (_that) {
case _StatoCheckout():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _StatoCheckout value)?  $default,){
final _that = this;
switch (_that) {
case _StatoCheckout() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String checkoutId,  String stato,  String piano,  String nome,  String tipo,  bool? prova,  bool? cambio,  String? esito)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _StatoCheckout() when $default != null:
return $default(_that.checkoutId,_that.stato,_that.piano,_that.nome,_that.tipo,_that.prova,_that.cambio,_that.esito);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String checkoutId,  String stato,  String piano,  String nome,  String tipo,  bool? prova,  bool? cambio,  String? esito)  $default,) {final _that = this;
switch (_that) {
case _StatoCheckout():
return $default(_that.checkoutId,_that.stato,_that.piano,_that.nome,_that.tipo,_that.prova,_that.cambio,_that.esito);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String checkoutId,  String stato,  String piano,  String nome,  String tipo,  bool? prova,  bool? cambio,  String? esito)?  $default,) {final _that = this;
switch (_that) {
case _StatoCheckout() when $default != null:
return $default(_that.checkoutId,_that.stato,_that.piano,_that.nome,_that.tipo,_that.prova,_that.cambio,_that.esito);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _StatoCheckout implements StatoCheckout {
  const _StatoCheckout({required this.checkoutId, required this.stato, required this.piano, required this.nome, required this.tipo, this.prova, this.cambio, this.esito});
  factory _StatoCheckout.fromJson(Map<String, dynamic> json) => _$StatoCheckoutFromJson(json);

@override final  String checkoutId;
@override final  String stato;
@override final  String piano;
@override final  String nome;
@override final  String tipo;
@override final  bool? prova;
@override final  bool? cambio;
@override final  String? esito;

/// Create a copy of StatoCheckout
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$StatoCheckoutCopyWith<_StatoCheckout> get copyWith => __$StatoCheckoutCopyWithImpl<_StatoCheckout>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$StatoCheckoutToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _StatoCheckout&&(identical(other.checkoutId, checkoutId) || other.checkoutId == checkoutId)&&(identical(other.stato, stato) || other.stato == stato)&&(identical(other.piano, piano) || other.piano == piano)&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.tipo, tipo) || other.tipo == tipo)&&(identical(other.prova, prova) || other.prova == prova)&&(identical(other.cambio, cambio) || other.cambio == cambio)&&(identical(other.esito, esito) || other.esito == esito));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,checkoutId,stato,piano,nome,tipo,prova,cambio,esito);
}

@override
String toString() {
    return 'StatoCheckout(checkoutId: $checkoutId, stato: $stato, piano: $piano, nome: $nome, tipo: $tipo, prova: $prova, cambio: $cambio, esito: $esito)';
}


}

/// @nodoc
abstract mixin class _$StatoCheckoutCopyWith<$Res> implements $StatoCheckoutCopyWith<$Res> {
  factory _$StatoCheckoutCopyWith(_StatoCheckout value, $Res Function(_StatoCheckout) _then) = __$StatoCheckoutCopyWithImpl;
@override @useResult
$Res call({
 String checkoutId, String stato, String piano, String nome, String tipo, bool? prova, bool? cambio, String? esito
});




}
/// @nodoc
class __$StatoCheckoutCopyWithImpl<$Res>
    implements _$StatoCheckoutCopyWith<$Res> {
  __$StatoCheckoutCopyWithImpl(this._self, this._then);

  final _StatoCheckout _self;
  final $Res Function(_StatoCheckout) _then;

/// Create a copy of StatoCheckout
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? checkoutId = null,Object? stato = null,Object? piano = null,Object? nome = null,Object? tipo = null,Object? prova = freezed,Object? cambio = freezed,Object? esito = freezed,}) {
  return _then(_StatoCheckout(
checkoutId: null == checkoutId ? _self.checkoutId : checkoutId // ignore: cast_nullable_to_non_nullable
as String,stato: null == stato ? _self.stato : stato // ignore: cast_nullable_to_non_nullable
as String,piano: null == piano ? _self.piano : piano // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,prova: freezed == prova ? _self.prova : prova // ignore: cast_nullable_to_non_nullable
as bool?,cambio: freezed == cambio ? _self.cambio : cambio // ignore: cast_nullable_to_non_nullable
as bool?,esito: freezed == esito ? _self.esito : esito // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$PianoSuccessivo {

 String get piano; String get nome; bool get annuale; String get dal;
/// Create a copy of PianoSuccessivo
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PianoSuccessivoCopyWith<PianoSuccessivo> get copyWith => _$PianoSuccessivoCopyWithImpl<PianoSuccessivo>(this as PianoSuccessivo, _$identity);

  /// Serializes this PianoSuccessivo to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as PianoSuccessivo;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PianoSuccessivo&&(identical(other.piano, _this.piano) || other.piano == _this.piano)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.annuale, _this.annuale) || other.annuale == _this.annuale)&&(identical(other.dal, _this.dal) || other.dal == _this.dal));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as PianoSuccessivo;
  return Object.hash(runtimeType,_this.piano,_this.nome,_this.annuale,_this.dal);
}

@override
String toString() {
  final _this = this as PianoSuccessivo;
  return 'PianoSuccessivo(piano: ${_this.piano}, nome: ${_this.nome}, annuale: ${_this.annuale}, dal: ${_this.dal})';
}


}

/// @nodoc
abstract mixin class $PianoSuccessivoCopyWith<$Res>  {
  factory $PianoSuccessivoCopyWith(PianoSuccessivo value, $Res Function(PianoSuccessivo) _then) = _$PianoSuccessivoCopyWithImpl;
@useResult
$Res call({
 String piano, String nome, bool annuale, String dal
});




}
/// @nodoc
class _$PianoSuccessivoCopyWithImpl<$Res>
    implements $PianoSuccessivoCopyWith<$Res> {
  _$PianoSuccessivoCopyWithImpl(this._self, this._then);

  final PianoSuccessivo _self;
  final $Res Function(PianoSuccessivo) _then;

/// Create a copy of PianoSuccessivo
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? piano = null,Object? nome = null,Object? annuale = null,Object? dal = null,}) {
  return _then(PianoSuccessivo(
piano: null == piano ? _self.piano : piano // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,annuale: null == annuale ? _self.annuale : annuale // ignore: cast_nullable_to_non_nullable
as bool,dal: null == dal ? _self.dal : dal // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [PianoSuccessivo].
extension PianoSuccessivoPatterns on PianoSuccessivo {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PianoSuccessivo value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PianoSuccessivo() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PianoSuccessivo value)  $default,){
final _that = this;
switch (_that) {
case _PianoSuccessivo():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PianoSuccessivo value)?  $default,){
final _that = this;
switch (_that) {
case _PianoSuccessivo() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String piano,  String nome,  bool annuale,  String dal)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PianoSuccessivo() when $default != null:
return $default(_that.piano,_that.nome,_that.annuale,_that.dal);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String piano,  String nome,  bool annuale,  String dal)  $default,) {final _that = this;
switch (_that) {
case _PianoSuccessivo():
return $default(_that.piano,_that.nome,_that.annuale,_that.dal);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String piano,  String nome,  bool annuale,  String dal)?  $default,) {final _that = this;
switch (_that) {
case _PianoSuccessivo() when $default != null:
return $default(_that.piano,_that.nome,_that.annuale,_that.dal);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _PianoSuccessivo implements PianoSuccessivo {
  const _PianoSuccessivo({required this.piano, required this.nome, this.annuale = false, required this.dal});
  factory _PianoSuccessivo.fromJson(Map<String, dynamic> json) => _$PianoSuccessivoFromJson(json);

@override final  String piano;
@override final  String nome;
@override@JsonKey() final  bool annuale;
@override final  String dal;

/// Create a copy of PianoSuccessivo
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PianoSuccessivoCopyWith<_PianoSuccessivo> get copyWith => __$PianoSuccessivoCopyWithImpl<_PianoSuccessivo>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PianoSuccessivoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _PianoSuccessivo&&(identical(other.piano, piano) || other.piano == piano)&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.annuale, annuale) || other.annuale == annuale)&&(identical(other.dal, dal) || other.dal == dal));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,piano,nome,annuale,dal);
}

@override
String toString() {
    return 'PianoSuccessivo(piano: $piano, nome: $nome, annuale: $annuale, dal: $dal)';
}


}

/// @nodoc
abstract mixin class _$PianoSuccessivoCopyWith<$Res> implements $PianoSuccessivoCopyWith<$Res> {
  factory _$PianoSuccessivoCopyWith(_PianoSuccessivo value, $Res Function(_PianoSuccessivo) _then) = __$PianoSuccessivoCopyWithImpl;
@override @useResult
$Res call({
 String piano, String nome, bool annuale, String dal
});




}
/// @nodoc
class __$PianoSuccessivoCopyWithImpl<$Res>
    implements _$PianoSuccessivoCopyWith<$Res> {
  __$PianoSuccessivoCopyWithImpl(this._self, this._then);

  final _PianoSuccessivo _self;
  final $Res Function(_PianoSuccessivo) _then;

/// Create a copy of PianoSuccessivo
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? piano = null,Object? nome = null,Object? annuale = null,Object? dal = null,}) {
  return _then(_PianoSuccessivo(
piano: null == piano ? _self.piano : piano // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,annuale: null == annuale ? _self.annuale : annuale // ignore: cast_nullable_to_non_nullable
as bool,dal: null == dal ? _self.dal : dal // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$CouponAbbonamento {

 String get codice; String get tipo; num get valore; bool get cumulabile; num get sconto; bool get perSempre; int? get rinnoviRimasti;
/// Create a copy of CouponAbbonamento
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CouponAbbonamentoCopyWith<CouponAbbonamento> get copyWith => _$CouponAbbonamentoCopyWithImpl<CouponAbbonamento>(this as CouponAbbonamento, _$identity);

  /// Serializes this CouponAbbonamento to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as CouponAbbonamento;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CouponAbbonamento&&(identical(other.codice, _this.codice) || other.codice == _this.codice)&&(identical(other.tipo, _this.tipo) || other.tipo == _this.tipo)&&(identical(other.valore, _this.valore) || other.valore == _this.valore)&&(identical(other.cumulabile, _this.cumulabile) || other.cumulabile == _this.cumulabile)&&(identical(other.sconto, _this.sconto) || other.sconto == _this.sconto)&&(identical(other.perSempre, _this.perSempre) || other.perSempre == _this.perSempre)&&(identical(other.rinnoviRimasti, _this.rinnoviRimasti) || other.rinnoviRimasti == _this.rinnoviRimasti));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as CouponAbbonamento;
  return Object.hash(runtimeType,_this.codice,_this.tipo,_this.valore,_this.cumulabile,_this.sconto,_this.perSempre,_this.rinnoviRimasti);
}

@override
String toString() {
  final _this = this as CouponAbbonamento;
  return 'CouponAbbonamento(codice: ${_this.codice}, tipo: ${_this.tipo}, valore: ${_this.valore}, cumulabile: ${_this.cumulabile}, sconto: ${_this.sconto}, perSempre: ${_this.perSempre}, rinnoviRimasti: ${_this.rinnoviRimasti})';
}


}

/// @nodoc
abstract mixin class $CouponAbbonamentoCopyWith<$Res>  {
  factory $CouponAbbonamentoCopyWith(CouponAbbonamento value, $Res Function(CouponAbbonamento) _then) = _$CouponAbbonamentoCopyWithImpl;
@useResult
$Res call({
 String codice, String tipo, num valore, bool cumulabile, num sconto, bool perSempre, int? rinnoviRimasti
});




}
/// @nodoc
class _$CouponAbbonamentoCopyWithImpl<$Res>
    implements $CouponAbbonamentoCopyWith<$Res> {
  _$CouponAbbonamentoCopyWithImpl(this._self, this._then);

  final CouponAbbonamento _self;
  final $Res Function(CouponAbbonamento) _then;

/// Create a copy of CouponAbbonamento
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? codice = null,Object? tipo = null,Object? valore = null,Object? cumulabile = null,Object? sconto = null,Object? perSempre = null,Object? rinnoviRimasti = freezed,}) {
  return _then(CouponAbbonamento(
codice: null == codice ? _self.codice : codice // ignore: cast_nullable_to_non_nullable
as String,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,valore: null == valore ? _self.valore : valore // ignore: cast_nullable_to_non_nullable
as num,cumulabile: null == cumulabile ? _self.cumulabile : cumulabile // ignore: cast_nullable_to_non_nullable
as bool,sconto: null == sconto ? _self.sconto : sconto // ignore: cast_nullable_to_non_nullable
as num,perSempre: null == perSempre ? _self.perSempre : perSempre // ignore: cast_nullable_to_non_nullable
as bool,rinnoviRimasti: freezed == rinnoviRimasti ? _self.rinnoviRimasti : rinnoviRimasti // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}

}


/// Adds pattern-matching-related methods to [CouponAbbonamento].
extension CouponAbbonamentoPatterns on CouponAbbonamento {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CouponAbbonamento value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CouponAbbonamento() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CouponAbbonamento value)  $default,){
final _that = this;
switch (_that) {
case _CouponAbbonamento():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CouponAbbonamento value)?  $default,){
final _that = this;
switch (_that) {
case _CouponAbbonamento() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String codice,  String tipo,  num valore,  bool cumulabile,  num sconto,  bool perSempre,  int? rinnoviRimasti)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CouponAbbonamento() when $default != null:
return $default(_that.codice,_that.tipo,_that.valore,_that.cumulabile,_that.sconto,_that.perSempre,_that.rinnoviRimasti);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String codice,  String tipo,  num valore,  bool cumulabile,  num sconto,  bool perSempre,  int? rinnoviRimasti)  $default,) {final _that = this;
switch (_that) {
case _CouponAbbonamento():
return $default(_that.codice,_that.tipo,_that.valore,_that.cumulabile,_that.sconto,_that.perSempre,_that.rinnoviRimasti);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String codice,  String tipo,  num valore,  bool cumulabile,  num sconto,  bool perSempre,  int? rinnoviRimasti)?  $default,) {final _that = this;
switch (_that) {
case _CouponAbbonamento() when $default != null:
return $default(_that.codice,_that.tipo,_that.valore,_that.cumulabile,_that.sconto,_that.perSempre,_that.rinnoviRimasti);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CouponAbbonamento implements CouponAbbonamento {
  const _CouponAbbonamento({required this.codice, required this.tipo, required this.valore, this.cumulabile = false, this.sconto = 0, this.perSempre = false, this.rinnoviRimasti});
  factory _CouponAbbonamento.fromJson(Map<String, dynamic> json) => _$CouponAbbonamentoFromJson(json);

@override final  String codice;
@override final  String tipo;
@override final  num valore;
@override@JsonKey() final  bool cumulabile;
@override@JsonKey() final  num sconto;
@override@JsonKey() final  bool perSempre;
@override final  int? rinnoviRimasti;

/// Create a copy of CouponAbbonamento
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CouponAbbonamentoCopyWith<_CouponAbbonamento> get copyWith => __$CouponAbbonamentoCopyWithImpl<_CouponAbbonamento>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CouponAbbonamentoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _CouponAbbonamento&&(identical(other.codice, codice) || other.codice == codice)&&(identical(other.tipo, tipo) || other.tipo == tipo)&&(identical(other.valore, valore) || other.valore == valore)&&(identical(other.cumulabile, cumulabile) || other.cumulabile == cumulabile)&&(identical(other.sconto, sconto) || other.sconto == sconto)&&(identical(other.perSempre, perSempre) || other.perSempre == perSempre)&&(identical(other.rinnoviRimasti, rinnoviRimasti) || other.rinnoviRimasti == rinnoviRimasti));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,codice,tipo,valore,cumulabile,sconto,perSempre,rinnoviRimasti);
}

@override
String toString() {
    return 'CouponAbbonamento(codice: $codice, tipo: $tipo, valore: $valore, cumulabile: $cumulabile, sconto: $sconto, perSempre: $perSempre, rinnoviRimasti: $rinnoviRimasti)';
}


}

/// @nodoc
abstract mixin class _$CouponAbbonamentoCopyWith<$Res> implements $CouponAbbonamentoCopyWith<$Res> {
  factory _$CouponAbbonamentoCopyWith(_CouponAbbonamento value, $Res Function(_CouponAbbonamento) _then) = __$CouponAbbonamentoCopyWithImpl;
@override @useResult
$Res call({
 String codice, String tipo, num valore, bool cumulabile, num sconto, bool perSempre, int? rinnoviRimasti
});




}
/// @nodoc
class __$CouponAbbonamentoCopyWithImpl<$Res>
    implements _$CouponAbbonamentoCopyWith<$Res> {
  __$CouponAbbonamentoCopyWithImpl(this._self, this._then);

  final _CouponAbbonamento _self;
  final $Res Function(_CouponAbbonamento) _then;

/// Create a copy of CouponAbbonamento
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? codice = null,Object? tipo = null,Object? valore = null,Object? cumulabile = null,Object? sconto = null,Object? perSempre = null,Object? rinnoviRimasti = freezed,}) {
  return _then(_CouponAbbonamento(
codice: null == codice ? _self.codice : codice // ignore: cast_nullable_to_non_nullable
as String,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,valore: null == valore ? _self.valore : valore // ignore: cast_nullable_to_non_nullable
as num,cumulabile: null == cumulabile ? _self.cumulabile : cumulabile // ignore: cast_nullable_to_non_nullable
as bool,sconto: null == sconto ? _self.sconto : sconto // ignore: cast_nullable_to_non_nullable
as num,perSempre: null == perSempre ? _self.perSempre : perSempre // ignore: cast_nullable_to_non_nullable
as bool,rinnoviRimasti: freezed == rinnoviRimasti ? _self.rinnoviRimasti : rinnoviRimasti // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}


}


/// @nodoc
mixin _$AbbonamentoDettaglio {

 String get id; String get piano; String get nome;/// `in_prova`, `attivo`, `in_sospeso`, `sospeso`, `disdetto`, `scaduto`.
 String get stato; String get provider; bool get store; String? get gestioneStore; bool get gratuito; bool get annuale; bool get prova; String get periodoInizio; String get periodoFine; String? get disdettoIl; bool get rinnovoAutomatico; int? get listino; int? get importoPeriodo; num get scontoRicorrente; int? get prossimoRinnovo; String get valuta; bool get fatturaAperta; String? get pagamentoFallitoIl; String? get fineTolleranza; PianoSuccessivo? get pianoSuccessivo; CouponAbbonamento? get coupon;
/// Create a copy of AbbonamentoDettaglio
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AbbonamentoDettaglioCopyWith<AbbonamentoDettaglio> get copyWith => _$AbbonamentoDettaglioCopyWithImpl<AbbonamentoDettaglio>(this as AbbonamentoDettaglio, _$identity);

  /// Serializes this AbbonamentoDettaglio to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as AbbonamentoDettaglio;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AbbonamentoDettaglio&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.piano, _this.piano) || other.piano == _this.piano)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.stato, _this.stato) || other.stato == _this.stato)&&(identical(other.provider, _this.provider) || other.provider == _this.provider)&&(identical(other.store, _this.store) || other.store == _this.store)&&(identical(other.gestioneStore, _this.gestioneStore) || other.gestioneStore == _this.gestioneStore)&&(identical(other.gratuito, _this.gratuito) || other.gratuito == _this.gratuito)&&(identical(other.annuale, _this.annuale) || other.annuale == _this.annuale)&&(identical(other.prova, _this.prova) || other.prova == _this.prova)&&(identical(other.periodoInizio, _this.periodoInizio) || other.periodoInizio == _this.periodoInizio)&&(identical(other.periodoFine, _this.periodoFine) || other.periodoFine == _this.periodoFine)&&(identical(other.disdettoIl, _this.disdettoIl) || other.disdettoIl == _this.disdettoIl)&&(identical(other.rinnovoAutomatico, _this.rinnovoAutomatico) || other.rinnovoAutomatico == _this.rinnovoAutomatico)&&(identical(other.listino, _this.listino) || other.listino == _this.listino)&&(identical(other.importoPeriodo, _this.importoPeriodo) || other.importoPeriodo == _this.importoPeriodo)&&(identical(other.scontoRicorrente, _this.scontoRicorrente) || other.scontoRicorrente == _this.scontoRicorrente)&&(identical(other.prossimoRinnovo, _this.prossimoRinnovo) || other.prossimoRinnovo == _this.prossimoRinnovo)&&(identical(other.valuta, _this.valuta) || other.valuta == _this.valuta)&&(identical(other.fatturaAperta, _this.fatturaAperta) || other.fatturaAperta == _this.fatturaAperta)&&(identical(other.pagamentoFallitoIl, _this.pagamentoFallitoIl) || other.pagamentoFallitoIl == _this.pagamentoFallitoIl)&&(identical(other.fineTolleranza, _this.fineTolleranza) || other.fineTolleranza == _this.fineTolleranza)&&(identical(other.pianoSuccessivo, _this.pianoSuccessivo) || other.pianoSuccessivo == _this.pianoSuccessivo)&&(identical(other.coupon, _this.coupon) || other.coupon == _this.coupon));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as AbbonamentoDettaglio;
  return Object.hashAll([runtimeType,_this.id,_this.piano,_this.nome,_this.stato,_this.provider,_this.store,_this.gestioneStore,_this.gratuito,_this.annuale,_this.prova,_this.periodoInizio,_this.periodoFine,_this.disdettoIl,_this.rinnovoAutomatico,_this.listino,_this.importoPeriodo,_this.scontoRicorrente,_this.prossimoRinnovo,_this.valuta,_this.fatturaAperta,_this.pagamentoFallitoIl,_this.fineTolleranza,_this.pianoSuccessivo,_this.coupon]);
}

@override
String toString() {
  final _this = this as AbbonamentoDettaglio;
  return 'AbbonamentoDettaglio(id: ${_this.id}, piano: ${_this.piano}, nome: ${_this.nome}, stato: ${_this.stato}, provider: ${_this.provider}, store: ${_this.store}, gestioneStore: ${_this.gestioneStore}, gratuito: ${_this.gratuito}, annuale: ${_this.annuale}, prova: ${_this.prova}, periodoInizio: ${_this.periodoInizio}, periodoFine: ${_this.periodoFine}, disdettoIl: ${_this.disdettoIl}, rinnovoAutomatico: ${_this.rinnovoAutomatico}, listino: ${_this.listino}, importoPeriodo: ${_this.importoPeriodo}, scontoRicorrente: ${_this.scontoRicorrente}, prossimoRinnovo: ${_this.prossimoRinnovo}, valuta: ${_this.valuta}, fatturaAperta: ${_this.fatturaAperta}, pagamentoFallitoIl: ${_this.pagamentoFallitoIl}, fineTolleranza: ${_this.fineTolleranza}, pianoSuccessivo: ${_this.pianoSuccessivo}, coupon: ${_this.coupon})';
}


}

/// @nodoc
abstract mixin class $AbbonamentoDettaglioCopyWith<$Res>  {
  factory $AbbonamentoDettaglioCopyWith(AbbonamentoDettaglio value, $Res Function(AbbonamentoDettaglio) _then) = _$AbbonamentoDettaglioCopyWithImpl;
@useResult
$Res call({
 String id, String piano, String nome, String stato, String provider, bool store, String? gestioneStore, bool gratuito, bool annuale, bool prova, String periodoInizio, String periodoFine, String? disdettoIl, bool rinnovoAutomatico, int? listino, int? importoPeriodo, num scontoRicorrente, int? prossimoRinnovo, String valuta, bool fatturaAperta, String? pagamentoFallitoIl, String? fineTolleranza, PianoSuccessivo? pianoSuccessivo, CouponAbbonamento? coupon
});


$PianoSuccessivoCopyWith<$Res>? get pianoSuccessivo;$CouponAbbonamentoCopyWith<$Res>? get coupon;

}
/// @nodoc
class _$AbbonamentoDettaglioCopyWithImpl<$Res>
    implements $AbbonamentoDettaglioCopyWith<$Res> {
  _$AbbonamentoDettaglioCopyWithImpl(this._self, this._then);

  final AbbonamentoDettaglio _self;
  final $Res Function(AbbonamentoDettaglio) _then;

/// Create a copy of AbbonamentoDettaglio
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? piano = null,Object? nome = null,Object? stato = null,Object? provider = null,Object? store = null,Object? gestioneStore = freezed,Object? gratuito = null,Object? annuale = null,Object? prova = null,Object? periodoInizio = null,Object? periodoFine = null,Object? disdettoIl = freezed,Object? rinnovoAutomatico = null,Object? listino = freezed,Object? importoPeriodo = freezed,Object? scontoRicorrente = null,Object? prossimoRinnovo = freezed,Object? valuta = null,Object? fatturaAperta = null,Object? pagamentoFallitoIl = freezed,Object? fineTolleranza = freezed,Object? pianoSuccessivo = freezed,Object? coupon = freezed,}) {
  return _then(AbbonamentoDettaglio(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,piano: null == piano ? _self.piano : piano // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,stato: null == stato ? _self.stato : stato // ignore: cast_nullable_to_non_nullable
as String,provider: null == provider ? _self.provider : provider // ignore: cast_nullable_to_non_nullable
as String,store: null == store ? _self.store : store // ignore: cast_nullable_to_non_nullable
as bool,gestioneStore: freezed == gestioneStore ? _self.gestioneStore : gestioneStore // ignore: cast_nullable_to_non_nullable
as String?,gratuito: null == gratuito ? _self.gratuito : gratuito // ignore: cast_nullable_to_non_nullable
as bool,annuale: null == annuale ? _self.annuale : annuale // ignore: cast_nullable_to_non_nullable
as bool,prova: null == prova ? _self.prova : prova // ignore: cast_nullable_to_non_nullable
as bool,periodoInizio: null == periodoInizio ? _self.periodoInizio : periodoInizio // ignore: cast_nullable_to_non_nullable
as String,periodoFine: null == periodoFine ? _self.periodoFine : periodoFine // ignore: cast_nullable_to_non_nullable
as String,disdettoIl: freezed == disdettoIl ? _self.disdettoIl : disdettoIl // ignore: cast_nullable_to_non_nullable
as String?,rinnovoAutomatico: null == rinnovoAutomatico ? _self.rinnovoAutomatico : rinnovoAutomatico // ignore: cast_nullable_to_non_nullable
as bool,listino: freezed == listino ? _self.listino : listino // ignore: cast_nullable_to_non_nullable
as int?,importoPeriodo: freezed == importoPeriodo ? _self.importoPeriodo : importoPeriodo // ignore: cast_nullable_to_non_nullable
as int?,scontoRicorrente: null == scontoRicorrente ? _self.scontoRicorrente : scontoRicorrente // ignore: cast_nullable_to_non_nullable
as num,prossimoRinnovo: freezed == prossimoRinnovo ? _self.prossimoRinnovo : prossimoRinnovo // ignore: cast_nullable_to_non_nullable
as int?,valuta: null == valuta ? _self.valuta : valuta // ignore: cast_nullable_to_non_nullable
as String,fatturaAperta: null == fatturaAperta ? _self.fatturaAperta : fatturaAperta // ignore: cast_nullable_to_non_nullable
as bool,pagamentoFallitoIl: freezed == pagamentoFallitoIl ? _self.pagamentoFallitoIl : pagamentoFallitoIl // ignore: cast_nullable_to_non_nullable
as String?,fineTolleranza: freezed == fineTolleranza ? _self.fineTolleranza : fineTolleranza // ignore: cast_nullable_to_non_nullable
as String?,pianoSuccessivo: freezed == pianoSuccessivo ? _self.pianoSuccessivo : pianoSuccessivo // ignore: cast_nullable_to_non_nullable
as PianoSuccessivo?,coupon: freezed == coupon ? _self.coupon : coupon // ignore: cast_nullable_to_non_nullable
as CouponAbbonamento?,
  ));
}
/// Create a copy of AbbonamentoDettaglio
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PianoSuccessivoCopyWith<$Res>? get pianoSuccessivo {
    if (_self.pianoSuccessivo == null) {
    return null;
  }

  return $PianoSuccessivoCopyWith<$Res>(_self.pianoSuccessivo!, (value) {
    return _then(_self.copyWith(pianoSuccessivo: value));
  });
}/// Create a copy of AbbonamentoDettaglio
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CouponAbbonamentoCopyWith<$Res>? get coupon {
    if (_self.coupon == null) {
    return null;
  }

  return $CouponAbbonamentoCopyWith<$Res>(_self.coupon!, (value) {
    return _then(_self.copyWith(coupon: value));
  });
}
}


/// Adds pattern-matching-related methods to [AbbonamentoDettaglio].
extension AbbonamentoDettaglioPatterns on AbbonamentoDettaglio {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _AbbonamentoDettaglio value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _AbbonamentoDettaglio() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _AbbonamentoDettaglio value)  $default,){
final _that = this;
switch (_that) {
case _AbbonamentoDettaglio():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _AbbonamentoDettaglio value)?  $default,){
final _that = this;
switch (_that) {
case _AbbonamentoDettaglio() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String piano,  String nome,  String stato,  String provider,  bool store,  String? gestioneStore,  bool gratuito,  bool annuale,  bool prova,  String periodoInizio,  String periodoFine,  String? disdettoIl,  bool rinnovoAutomatico,  int? listino,  int? importoPeriodo,  num scontoRicorrente,  int? prossimoRinnovo,  String valuta,  bool fatturaAperta,  String? pagamentoFallitoIl,  String? fineTolleranza,  PianoSuccessivo? pianoSuccessivo,  CouponAbbonamento? coupon)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _AbbonamentoDettaglio() when $default != null:
return $default(_that.id,_that.piano,_that.nome,_that.stato,_that.provider,_that.store,_that.gestioneStore,_that.gratuito,_that.annuale,_that.prova,_that.periodoInizio,_that.periodoFine,_that.disdettoIl,_that.rinnovoAutomatico,_that.listino,_that.importoPeriodo,_that.scontoRicorrente,_that.prossimoRinnovo,_that.valuta,_that.fatturaAperta,_that.pagamentoFallitoIl,_that.fineTolleranza,_that.pianoSuccessivo,_that.coupon);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String piano,  String nome,  String stato,  String provider,  bool store,  String? gestioneStore,  bool gratuito,  bool annuale,  bool prova,  String periodoInizio,  String periodoFine,  String? disdettoIl,  bool rinnovoAutomatico,  int? listino,  int? importoPeriodo,  num scontoRicorrente,  int? prossimoRinnovo,  String valuta,  bool fatturaAperta,  String? pagamentoFallitoIl,  String? fineTolleranza,  PianoSuccessivo? pianoSuccessivo,  CouponAbbonamento? coupon)  $default,) {final _that = this;
switch (_that) {
case _AbbonamentoDettaglio():
return $default(_that.id,_that.piano,_that.nome,_that.stato,_that.provider,_that.store,_that.gestioneStore,_that.gratuito,_that.annuale,_that.prova,_that.periodoInizio,_that.periodoFine,_that.disdettoIl,_that.rinnovoAutomatico,_that.listino,_that.importoPeriodo,_that.scontoRicorrente,_that.prossimoRinnovo,_that.valuta,_that.fatturaAperta,_that.pagamentoFallitoIl,_that.fineTolleranza,_that.pianoSuccessivo,_that.coupon);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String piano,  String nome,  String stato,  String provider,  bool store,  String? gestioneStore,  bool gratuito,  bool annuale,  bool prova,  String periodoInizio,  String periodoFine,  String? disdettoIl,  bool rinnovoAutomatico,  int? listino,  int? importoPeriodo,  num scontoRicorrente,  int? prossimoRinnovo,  String valuta,  bool fatturaAperta,  String? pagamentoFallitoIl,  String? fineTolleranza,  PianoSuccessivo? pianoSuccessivo,  CouponAbbonamento? coupon)?  $default,) {final _that = this;
switch (_that) {
case _AbbonamentoDettaglio() when $default != null:
return $default(_that.id,_that.piano,_that.nome,_that.stato,_that.provider,_that.store,_that.gestioneStore,_that.gratuito,_that.annuale,_that.prova,_that.periodoInizio,_that.periodoFine,_that.disdettoIl,_that.rinnovoAutomatico,_that.listino,_that.importoPeriodo,_that.scontoRicorrente,_that.prossimoRinnovo,_that.valuta,_that.fatturaAperta,_that.pagamentoFallitoIl,_that.fineTolleranza,_that.pianoSuccessivo,_that.coupon);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _AbbonamentoDettaglio implements AbbonamentoDettaglio {
  const _AbbonamentoDettaglio({required this.id, required this.piano, required this.nome, required this.stato, required this.provider, this.store = false, this.gestioneStore, this.gratuito = false, this.annuale = false, this.prova = false, required this.periodoInizio, required this.periodoFine, this.disdettoIl, this.rinnovoAutomatico = false, this.listino, this.importoPeriodo, this.scontoRicorrente = 0, this.prossimoRinnovo, this.valuta = 'EUR', this.fatturaAperta = false, this.pagamentoFallitoIl, this.fineTolleranza, this.pianoSuccessivo, this.coupon});
  factory _AbbonamentoDettaglio.fromJson(Map<String, dynamic> json) => _$AbbonamentoDettaglioFromJson(json);

@override final  String id;
@override final  String piano;
@override final  String nome;
/// `in_prova`, `attivo`, `in_sospeso`, `sospeso`, `disdetto`, `scaduto`.
@override final  String stato;
@override final  String provider;
@override@JsonKey() final  bool store;
@override final  String? gestioneStore;
@override@JsonKey() final  bool gratuito;
@override@JsonKey() final  bool annuale;
@override@JsonKey() final  bool prova;
@override final  String periodoInizio;
@override final  String periodoFine;
@override final  String? disdettoIl;
@override@JsonKey() final  bool rinnovoAutomatico;
@override final  int? listino;
@override final  int? importoPeriodo;
@override@JsonKey() final  num scontoRicorrente;
@override final  int? prossimoRinnovo;
@override@JsonKey() final  String valuta;
@override@JsonKey() final  bool fatturaAperta;
@override final  String? pagamentoFallitoIl;
@override final  String? fineTolleranza;
@override final  PianoSuccessivo? pianoSuccessivo;
@override final  CouponAbbonamento? coupon;

/// Create a copy of AbbonamentoDettaglio
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$AbbonamentoDettaglioCopyWith<_AbbonamentoDettaglio> get copyWith => __$AbbonamentoDettaglioCopyWithImpl<_AbbonamentoDettaglio>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$AbbonamentoDettaglioToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _AbbonamentoDettaglio&&(identical(other.id, id) || other.id == id)&&(identical(other.piano, piano) || other.piano == piano)&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.stato, stato) || other.stato == stato)&&(identical(other.provider, provider) || other.provider == provider)&&(identical(other.store, store) || other.store == store)&&(identical(other.gestioneStore, gestioneStore) || other.gestioneStore == gestioneStore)&&(identical(other.gratuito, gratuito) || other.gratuito == gratuito)&&(identical(other.annuale, annuale) || other.annuale == annuale)&&(identical(other.prova, prova) || other.prova == prova)&&(identical(other.periodoInizio, periodoInizio) || other.periodoInizio == periodoInizio)&&(identical(other.periodoFine, periodoFine) || other.periodoFine == periodoFine)&&(identical(other.disdettoIl, disdettoIl) || other.disdettoIl == disdettoIl)&&(identical(other.rinnovoAutomatico, rinnovoAutomatico) || other.rinnovoAutomatico == rinnovoAutomatico)&&(identical(other.listino, listino) || other.listino == listino)&&(identical(other.importoPeriodo, importoPeriodo) || other.importoPeriodo == importoPeriodo)&&(identical(other.scontoRicorrente, scontoRicorrente) || other.scontoRicorrente == scontoRicorrente)&&(identical(other.prossimoRinnovo, prossimoRinnovo) || other.prossimoRinnovo == prossimoRinnovo)&&(identical(other.valuta, valuta) || other.valuta == valuta)&&(identical(other.fatturaAperta, fatturaAperta) || other.fatturaAperta == fatturaAperta)&&(identical(other.pagamentoFallitoIl, pagamentoFallitoIl) || other.pagamentoFallitoIl == pagamentoFallitoIl)&&(identical(other.fineTolleranza, fineTolleranza) || other.fineTolleranza == fineTolleranza)&&(identical(other.pianoSuccessivo, pianoSuccessivo) || other.pianoSuccessivo == pianoSuccessivo)&&(identical(other.coupon, coupon) || other.coupon == coupon));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hashAll([runtimeType,id,piano,nome,stato,provider,store,gestioneStore,gratuito,annuale,prova,periodoInizio,periodoFine,disdettoIl,rinnovoAutomatico,listino,importoPeriodo,scontoRicorrente,prossimoRinnovo,valuta,fatturaAperta,pagamentoFallitoIl,fineTolleranza,pianoSuccessivo,coupon]);
}

@override
String toString() {
    return 'AbbonamentoDettaglio(id: $id, piano: $piano, nome: $nome, stato: $stato, provider: $provider, store: $store, gestioneStore: $gestioneStore, gratuito: $gratuito, annuale: $annuale, prova: $prova, periodoInizio: $periodoInizio, periodoFine: $periodoFine, disdettoIl: $disdettoIl, rinnovoAutomatico: $rinnovoAutomatico, listino: $listino, importoPeriodo: $importoPeriodo, scontoRicorrente: $scontoRicorrente, prossimoRinnovo: $prossimoRinnovo, valuta: $valuta, fatturaAperta: $fatturaAperta, pagamentoFallitoIl: $pagamentoFallitoIl, fineTolleranza: $fineTolleranza, pianoSuccessivo: $pianoSuccessivo, coupon: $coupon)';
}


}

/// @nodoc
abstract mixin class _$AbbonamentoDettaglioCopyWith<$Res> implements $AbbonamentoDettaglioCopyWith<$Res> {
  factory _$AbbonamentoDettaglioCopyWith(_AbbonamentoDettaglio value, $Res Function(_AbbonamentoDettaglio) _then) = __$AbbonamentoDettaglioCopyWithImpl;
@override @useResult
$Res call({
 String id, String piano, String nome, String stato, String provider, bool store, String? gestioneStore, bool gratuito, bool annuale, bool prova, String periodoInizio, String periodoFine, String? disdettoIl, bool rinnovoAutomatico, int? listino, int? importoPeriodo, num scontoRicorrente, int? prossimoRinnovo, String valuta, bool fatturaAperta, String? pagamentoFallitoIl, String? fineTolleranza, PianoSuccessivo? pianoSuccessivo, CouponAbbonamento? coupon
});


@override $PianoSuccessivoCopyWith<$Res>? get pianoSuccessivo;@override $CouponAbbonamentoCopyWith<$Res>? get coupon;

}
/// @nodoc
class __$AbbonamentoDettaglioCopyWithImpl<$Res>
    implements _$AbbonamentoDettaglioCopyWith<$Res> {
  __$AbbonamentoDettaglioCopyWithImpl(this._self, this._then);

  final _AbbonamentoDettaglio _self;
  final $Res Function(_AbbonamentoDettaglio) _then;

/// Create a copy of AbbonamentoDettaglio
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? piano = null,Object? nome = null,Object? stato = null,Object? provider = null,Object? store = null,Object? gestioneStore = freezed,Object? gratuito = null,Object? annuale = null,Object? prova = null,Object? periodoInizio = null,Object? periodoFine = null,Object? disdettoIl = freezed,Object? rinnovoAutomatico = null,Object? listino = freezed,Object? importoPeriodo = freezed,Object? scontoRicorrente = null,Object? prossimoRinnovo = freezed,Object? valuta = null,Object? fatturaAperta = null,Object? pagamentoFallitoIl = freezed,Object? fineTolleranza = freezed,Object? pianoSuccessivo = freezed,Object? coupon = freezed,}) {
  return _then(_AbbonamentoDettaglio(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,piano: null == piano ? _self.piano : piano // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,stato: null == stato ? _self.stato : stato // ignore: cast_nullable_to_non_nullable
as String,provider: null == provider ? _self.provider : provider // ignore: cast_nullable_to_non_nullable
as String,store: null == store ? _self.store : store // ignore: cast_nullable_to_non_nullable
as bool,gestioneStore: freezed == gestioneStore ? _self.gestioneStore : gestioneStore // ignore: cast_nullable_to_non_nullable
as String?,gratuito: null == gratuito ? _self.gratuito : gratuito // ignore: cast_nullable_to_non_nullable
as bool,annuale: null == annuale ? _self.annuale : annuale // ignore: cast_nullable_to_non_nullable
as bool,prova: null == prova ? _self.prova : prova // ignore: cast_nullable_to_non_nullable
as bool,periodoInizio: null == periodoInizio ? _self.periodoInizio : periodoInizio // ignore: cast_nullable_to_non_nullable
as String,periodoFine: null == periodoFine ? _self.periodoFine : periodoFine // ignore: cast_nullable_to_non_nullable
as String,disdettoIl: freezed == disdettoIl ? _self.disdettoIl : disdettoIl // ignore: cast_nullable_to_non_nullable
as String?,rinnovoAutomatico: null == rinnovoAutomatico ? _self.rinnovoAutomatico : rinnovoAutomatico // ignore: cast_nullable_to_non_nullable
as bool,listino: freezed == listino ? _self.listino : listino // ignore: cast_nullable_to_non_nullable
as int?,importoPeriodo: freezed == importoPeriodo ? _self.importoPeriodo : importoPeriodo // ignore: cast_nullable_to_non_nullable
as int?,scontoRicorrente: null == scontoRicorrente ? _self.scontoRicorrente : scontoRicorrente // ignore: cast_nullable_to_non_nullable
as num,prossimoRinnovo: freezed == prossimoRinnovo ? _self.prossimoRinnovo : prossimoRinnovo // ignore: cast_nullable_to_non_nullable
as int?,valuta: null == valuta ? _self.valuta : valuta // ignore: cast_nullable_to_non_nullable
as String,fatturaAperta: null == fatturaAperta ? _self.fatturaAperta : fatturaAperta // ignore: cast_nullable_to_non_nullable
as bool,pagamentoFallitoIl: freezed == pagamentoFallitoIl ? _self.pagamentoFallitoIl : pagamentoFallitoIl // ignore: cast_nullable_to_non_nullable
as String?,fineTolleranza: freezed == fineTolleranza ? _self.fineTolleranza : fineTolleranza // ignore: cast_nullable_to_non_nullable
as String?,pianoSuccessivo: freezed == pianoSuccessivo ? _self.pianoSuccessivo : pianoSuccessivo // ignore: cast_nullable_to_non_nullable
as PianoSuccessivo?,coupon: freezed == coupon ? _self.coupon : coupon // ignore: cast_nullable_to_non_nullable
as CouponAbbonamento?,
  ));
}

/// Create a copy of AbbonamentoDettaglio
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PianoSuccessivoCopyWith<$Res>? get pianoSuccessivo {
    if (_self.pianoSuccessivo == null) {
    return null;
  }

  return $PianoSuccessivoCopyWith<$Res>(_self.pianoSuccessivo!, (value) {
    return _then(_self.copyWith(pianoSuccessivo: value));
  });
}/// Create a copy of AbbonamentoDettaglio
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CouponAbbonamentoCopyWith<$Res>? get coupon {
    if (_self.coupon == null) {
    return null;
  }

  return $CouponAbbonamentoCopyWith<$Res>(_self.coupon!, (value) {
    return _then(_self.copyWith(coupon: value));
  });
}
}


/// @nodoc
mixin _$ImpostazioniAbbonamenti {

 bool get bannerProva; bool get provaDisponibile; int get giorniProva; num get scontoProva; num get scontoRinnovo; int get condoniPerPeriodo; int get giorniPromemoriaProva; int get giorniTolleranza;
/// Create a copy of ImpostazioniAbbonamenti
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ImpostazioniAbbonamentiCopyWith<ImpostazioniAbbonamenti> get copyWith => _$ImpostazioniAbbonamentiCopyWithImpl<ImpostazioniAbbonamenti>(this as ImpostazioniAbbonamenti, _$identity);

  /// Serializes this ImpostazioniAbbonamenti to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as ImpostazioniAbbonamenti;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ImpostazioniAbbonamenti&&(identical(other.bannerProva, _this.bannerProva) || other.bannerProva == _this.bannerProva)&&(identical(other.provaDisponibile, _this.provaDisponibile) || other.provaDisponibile == _this.provaDisponibile)&&(identical(other.giorniProva, _this.giorniProva) || other.giorniProva == _this.giorniProva)&&(identical(other.scontoProva, _this.scontoProva) || other.scontoProva == _this.scontoProva)&&(identical(other.scontoRinnovo, _this.scontoRinnovo) || other.scontoRinnovo == _this.scontoRinnovo)&&(identical(other.condoniPerPeriodo, _this.condoniPerPeriodo) || other.condoniPerPeriodo == _this.condoniPerPeriodo)&&(identical(other.giorniPromemoriaProva, _this.giorniPromemoriaProva) || other.giorniPromemoriaProva == _this.giorniPromemoriaProva)&&(identical(other.giorniTolleranza, _this.giorniTolleranza) || other.giorniTolleranza == _this.giorniTolleranza));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as ImpostazioniAbbonamenti;
  return Object.hash(runtimeType,_this.bannerProva,_this.provaDisponibile,_this.giorniProva,_this.scontoProva,_this.scontoRinnovo,_this.condoniPerPeriodo,_this.giorniPromemoriaProva,_this.giorniTolleranza);
}

@override
String toString() {
  final _this = this as ImpostazioniAbbonamenti;
  return 'ImpostazioniAbbonamenti(bannerProva: ${_this.bannerProva}, provaDisponibile: ${_this.provaDisponibile}, giorniProva: ${_this.giorniProva}, scontoProva: ${_this.scontoProva}, scontoRinnovo: ${_this.scontoRinnovo}, condoniPerPeriodo: ${_this.condoniPerPeriodo}, giorniPromemoriaProva: ${_this.giorniPromemoriaProva}, giorniTolleranza: ${_this.giorniTolleranza})';
}


}

/// @nodoc
abstract mixin class $ImpostazioniAbbonamentiCopyWith<$Res>  {
  factory $ImpostazioniAbbonamentiCopyWith(ImpostazioniAbbonamenti value, $Res Function(ImpostazioniAbbonamenti) _then) = _$ImpostazioniAbbonamentiCopyWithImpl;
@useResult
$Res call({
 bool bannerProva, bool provaDisponibile, int giorniProva, num scontoProva, num scontoRinnovo, int condoniPerPeriodo, int giorniPromemoriaProva, int giorniTolleranza
});




}
/// @nodoc
class _$ImpostazioniAbbonamentiCopyWithImpl<$Res>
    implements $ImpostazioniAbbonamentiCopyWith<$Res> {
  _$ImpostazioniAbbonamentiCopyWithImpl(this._self, this._then);

  final ImpostazioniAbbonamenti _self;
  final $Res Function(ImpostazioniAbbonamenti) _then;

/// Create a copy of ImpostazioniAbbonamenti
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? bannerProva = null,Object? provaDisponibile = null,Object? giorniProva = null,Object? scontoProva = null,Object? scontoRinnovo = null,Object? condoniPerPeriodo = null,Object? giorniPromemoriaProva = null,Object? giorniTolleranza = null,}) {
  return _then(ImpostazioniAbbonamenti(
bannerProva: null == bannerProva ? _self.bannerProva : bannerProva // ignore: cast_nullable_to_non_nullable
as bool,provaDisponibile: null == provaDisponibile ? _self.provaDisponibile : provaDisponibile // ignore: cast_nullable_to_non_nullable
as bool,giorniProva: null == giorniProva ? _self.giorniProva : giorniProva // ignore: cast_nullable_to_non_nullable
as int,scontoProva: null == scontoProva ? _self.scontoProva : scontoProva // ignore: cast_nullable_to_non_nullable
as num,scontoRinnovo: null == scontoRinnovo ? _self.scontoRinnovo : scontoRinnovo // ignore: cast_nullable_to_non_nullable
as num,condoniPerPeriodo: null == condoniPerPeriodo ? _self.condoniPerPeriodo : condoniPerPeriodo // ignore: cast_nullable_to_non_nullable
as int,giorniPromemoriaProva: null == giorniPromemoriaProva ? _self.giorniPromemoriaProva : giorniPromemoriaProva // ignore: cast_nullable_to_non_nullable
as int,giorniTolleranza: null == giorniTolleranza ? _self.giorniTolleranza : giorniTolleranza // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [ImpostazioniAbbonamenti].
extension ImpostazioniAbbonamentiPatterns on ImpostazioniAbbonamenti {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ImpostazioniAbbonamenti value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ImpostazioniAbbonamenti() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ImpostazioniAbbonamenti value)  $default,){
final _that = this;
switch (_that) {
case _ImpostazioniAbbonamenti():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ImpostazioniAbbonamenti value)?  $default,){
final _that = this;
switch (_that) {
case _ImpostazioniAbbonamenti() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( bool bannerProva,  bool provaDisponibile,  int giorniProva,  num scontoProva,  num scontoRinnovo,  int condoniPerPeriodo,  int giorniPromemoriaProva,  int giorniTolleranza)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ImpostazioniAbbonamenti() when $default != null:
return $default(_that.bannerProva,_that.provaDisponibile,_that.giorniProva,_that.scontoProva,_that.scontoRinnovo,_that.condoniPerPeriodo,_that.giorniPromemoriaProva,_that.giorniTolleranza);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( bool bannerProva,  bool provaDisponibile,  int giorniProva,  num scontoProva,  num scontoRinnovo,  int condoniPerPeriodo,  int giorniPromemoriaProva,  int giorniTolleranza)  $default,) {final _that = this;
switch (_that) {
case _ImpostazioniAbbonamenti():
return $default(_that.bannerProva,_that.provaDisponibile,_that.giorniProva,_that.scontoProva,_that.scontoRinnovo,_that.condoniPerPeriodo,_that.giorniPromemoriaProva,_that.giorniTolleranza);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( bool bannerProva,  bool provaDisponibile,  int giorniProva,  num scontoProva,  num scontoRinnovo,  int condoniPerPeriodo,  int giorniPromemoriaProva,  int giorniTolleranza)?  $default,) {final _that = this;
switch (_that) {
case _ImpostazioniAbbonamenti() when $default != null:
return $default(_that.bannerProva,_that.provaDisponibile,_that.giorniProva,_that.scontoProva,_that.scontoRinnovo,_that.condoniPerPeriodo,_that.giorniPromemoriaProva,_that.giorniTolleranza);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ImpostazioniAbbonamenti implements ImpostazioniAbbonamenti {
  const _ImpostazioniAbbonamenti({this.bannerProva = false, this.provaDisponibile = false, this.giorniProva = 14, this.scontoProva = 50, this.scontoRinnovo = 20, this.condoniPerPeriodo = 2, this.giorniPromemoriaProva = 2, this.giorniTolleranza = 7});
  factory _ImpostazioniAbbonamenti.fromJson(Map<String, dynamic> json) => _$ImpostazioniAbbonamentiFromJson(json);

@override@JsonKey() final  bool bannerProva;
@override@JsonKey() final  bool provaDisponibile;
@override@JsonKey() final  int giorniProva;
@override@JsonKey() final  num scontoProva;
@override@JsonKey() final  num scontoRinnovo;
@override@JsonKey() final  int condoniPerPeriodo;
@override@JsonKey() final  int giorniPromemoriaProva;
@override@JsonKey() final  int giorniTolleranza;

/// Create a copy of ImpostazioniAbbonamenti
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ImpostazioniAbbonamentiCopyWith<_ImpostazioniAbbonamenti> get copyWith => __$ImpostazioniAbbonamentiCopyWithImpl<_ImpostazioniAbbonamenti>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ImpostazioniAbbonamentiToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _ImpostazioniAbbonamenti&&(identical(other.bannerProva, bannerProva) || other.bannerProva == bannerProva)&&(identical(other.provaDisponibile, provaDisponibile) || other.provaDisponibile == provaDisponibile)&&(identical(other.giorniProva, giorniProva) || other.giorniProva == giorniProva)&&(identical(other.scontoProva, scontoProva) || other.scontoProva == scontoProva)&&(identical(other.scontoRinnovo, scontoRinnovo) || other.scontoRinnovo == scontoRinnovo)&&(identical(other.condoniPerPeriodo, condoniPerPeriodo) || other.condoniPerPeriodo == condoniPerPeriodo)&&(identical(other.giorniPromemoriaProva, giorniPromemoriaProva) || other.giorniPromemoriaProva == giorniPromemoriaProva)&&(identical(other.giorniTolleranza, giorniTolleranza) || other.giorniTolleranza == giorniTolleranza));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,bannerProva,provaDisponibile,giorniProva,scontoProva,scontoRinnovo,condoniPerPeriodo,giorniPromemoriaProva,giorniTolleranza);
}

@override
String toString() {
    return 'ImpostazioniAbbonamenti(bannerProva: $bannerProva, provaDisponibile: $provaDisponibile, giorniProva: $giorniProva, scontoProva: $scontoProva, scontoRinnovo: $scontoRinnovo, condoniPerPeriodo: $condoniPerPeriodo, giorniPromemoriaProva: $giorniPromemoriaProva, giorniTolleranza: $giorniTolleranza)';
}


}

/// @nodoc
abstract mixin class _$ImpostazioniAbbonamentiCopyWith<$Res> implements $ImpostazioniAbbonamentiCopyWith<$Res> {
  factory _$ImpostazioniAbbonamentiCopyWith(_ImpostazioniAbbonamenti value, $Res Function(_ImpostazioniAbbonamenti) _then) = __$ImpostazioniAbbonamentiCopyWithImpl;
@override @useResult
$Res call({
 bool bannerProva, bool provaDisponibile, int giorniProva, num scontoProva, num scontoRinnovo, int condoniPerPeriodo, int giorniPromemoriaProva, int giorniTolleranza
});




}
/// @nodoc
class __$ImpostazioniAbbonamentiCopyWithImpl<$Res>
    implements _$ImpostazioniAbbonamentiCopyWith<$Res> {
  __$ImpostazioniAbbonamentiCopyWithImpl(this._self, this._then);

  final _ImpostazioniAbbonamenti _self;
  final $Res Function(_ImpostazioniAbbonamenti) _then;

/// Create a copy of ImpostazioniAbbonamenti
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? bannerProva = null,Object? provaDisponibile = null,Object? giorniProva = null,Object? scontoProva = null,Object? scontoRinnovo = null,Object? condoniPerPeriodo = null,Object? giorniPromemoriaProva = null,Object? giorniTolleranza = null,}) {
  return _then(_ImpostazioniAbbonamenti(
bannerProva: null == bannerProva ? _self.bannerProva : bannerProva // ignore: cast_nullable_to_non_nullable
as bool,provaDisponibile: null == provaDisponibile ? _self.provaDisponibile : provaDisponibile // ignore: cast_nullable_to_non_nullable
as bool,giorniProva: null == giorniProva ? _self.giorniProva : giorniProva // ignore: cast_nullable_to_non_nullable
as int,scontoProva: null == scontoProva ? _self.scontoProva : scontoProva // ignore: cast_nullable_to_non_nullable
as num,scontoRinnovo: null == scontoRinnovo ? _self.scontoRinnovo : scontoRinnovo // ignore: cast_nullable_to_non_nullable
as num,condoniPerPeriodo: null == condoniPerPeriodo ? _self.condoniPerPeriodo : condoniPerPeriodo // ignore: cast_nullable_to_non_nullable
as int,giorniPromemoriaProva: null == giorniPromemoriaProva ? _self.giorniPromemoriaProva : giorniPromemoriaProva // ignore: cast_nullable_to_non_nullable
as int,giorniTolleranza: null == giorniTolleranza ? _self.giorniTolleranza : giorniTolleranza // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$NumeriAbbonamento {

 num get scontoRinnovo; num get scontoProva; int get giorniProva; int get giorniTolleranza;
/// Create a copy of NumeriAbbonamento
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$NumeriAbbonamentoCopyWith<NumeriAbbonamento> get copyWith => _$NumeriAbbonamentoCopyWithImpl<NumeriAbbonamento>(this as NumeriAbbonamento, _$identity);

  /// Serializes this NumeriAbbonamento to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as NumeriAbbonamento;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is NumeriAbbonamento&&(identical(other.scontoRinnovo, _this.scontoRinnovo) || other.scontoRinnovo == _this.scontoRinnovo)&&(identical(other.scontoProva, _this.scontoProva) || other.scontoProva == _this.scontoProva)&&(identical(other.giorniProva, _this.giorniProva) || other.giorniProva == _this.giorniProva)&&(identical(other.giorniTolleranza, _this.giorniTolleranza) || other.giorniTolleranza == _this.giorniTolleranza));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as NumeriAbbonamento;
  return Object.hash(runtimeType,_this.scontoRinnovo,_this.scontoProva,_this.giorniProva,_this.giorniTolleranza);
}

@override
String toString() {
  final _this = this as NumeriAbbonamento;
  return 'NumeriAbbonamento(scontoRinnovo: ${_this.scontoRinnovo}, scontoProva: ${_this.scontoProva}, giorniProva: ${_this.giorniProva}, giorniTolleranza: ${_this.giorniTolleranza})';
}


}

/// @nodoc
abstract mixin class $NumeriAbbonamentoCopyWith<$Res>  {
  factory $NumeriAbbonamentoCopyWith(NumeriAbbonamento value, $Res Function(NumeriAbbonamento) _then) = _$NumeriAbbonamentoCopyWithImpl;
@useResult
$Res call({
 num scontoRinnovo, num scontoProva, int giorniProva, int giorniTolleranza
});




}
/// @nodoc
class _$NumeriAbbonamentoCopyWithImpl<$Res>
    implements $NumeriAbbonamentoCopyWith<$Res> {
  _$NumeriAbbonamentoCopyWithImpl(this._self, this._then);

  final NumeriAbbonamento _self;
  final $Res Function(NumeriAbbonamento) _then;

/// Create a copy of NumeriAbbonamento
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? scontoRinnovo = null,Object? scontoProva = null,Object? giorniProva = null,Object? giorniTolleranza = null,}) {
  return _then(NumeriAbbonamento(
scontoRinnovo: null == scontoRinnovo ? _self.scontoRinnovo : scontoRinnovo // ignore: cast_nullable_to_non_nullable
as num,scontoProva: null == scontoProva ? _self.scontoProva : scontoProva // ignore: cast_nullable_to_non_nullable
as num,giorniProva: null == giorniProva ? _self.giorniProva : giorniProva // ignore: cast_nullable_to_non_nullable
as int,giorniTolleranza: null == giorniTolleranza ? _self.giorniTolleranza : giorniTolleranza // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [NumeriAbbonamento].
extension NumeriAbbonamentoPatterns on NumeriAbbonamento {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _NumeriAbbonamento value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _NumeriAbbonamento() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _NumeriAbbonamento value)  $default,){
final _that = this;
switch (_that) {
case _NumeriAbbonamento():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _NumeriAbbonamento value)?  $default,){
final _that = this;
switch (_that) {
case _NumeriAbbonamento() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( num scontoRinnovo,  num scontoProva,  int giorniProva,  int giorniTolleranza)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _NumeriAbbonamento() when $default != null:
return $default(_that.scontoRinnovo,_that.scontoProva,_that.giorniProva,_that.giorniTolleranza);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( num scontoRinnovo,  num scontoProva,  int giorniProva,  int giorniTolleranza)  $default,) {final _that = this;
switch (_that) {
case _NumeriAbbonamento():
return $default(_that.scontoRinnovo,_that.scontoProva,_that.giorniProva,_that.giorniTolleranza);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( num scontoRinnovo,  num scontoProva,  int giorniProva,  int giorniTolleranza)?  $default,) {final _that = this;
switch (_that) {
case _NumeriAbbonamento() when $default != null:
return $default(_that.scontoRinnovo,_that.scontoProva,_that.giorniProva,_that.giorniTolleranza);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _NumeriAbbonamento implements NumeriAbbonamento {
  const _NumeriAbbonamento({this.scontoRinnovo = 20, this.scontoProva = 50, this.giorniProva = 14, this.giorniTolleranza = 7});
  factory _NumeriAbbonamento.fromJson(Map<String, dynamic> json) => _$NumeriAbbonamentoFromJson(json);

@override@JsonKey() final  num scontoRinnovo;
@override@JsonKey() final  num scontoProva;
@override@JsonKey() final  int giorniProva;
@override@JsonKey() final  int giorniTolleranza;

/// Create a copy of NumeriAbbonamento
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$NumeriAbbonamentoCopyWith<_NumeriAbbonamento> get copyWith => __$NumeriAbbonamentoCopyWithImpl<_NumeriAbbonamento>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$NumeriAbbonamentoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _NumeriAbbonamento&&(identical(other.scontoRinnovo, scontoRinnovo) || other.scontoRinnovo == scontoRinnovo)&&(identical(other.scontoProva, scontoProva) || other.scontoProva == scontoProva)&&(identical(other.giorniProva, giorniProva) || other.giorniProva == giorniProva)&&(identical(other.giorniTolleranza, giorniTolleranza) || other.giorniTolleranza == giorniTolleranza));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,scontoRinnovo,scontoProva,giorniProva,giorniTolleranza);
}

@override
String toString() {
    return 'NumeriAbbonamento(scontoRinnovo: $scontoRinnovo, scontoProva: $scontoProva, giorniProva: $giorniProva, giorniTolleranza: $giorniTolleranza)';
}


}

/// @nodoc
abstract mixin class _$NumeriAbbonamentoCopyWith<$Res> implements $NumeriAbbonamentoCopyWith<$Res> {
  factory _$NumeriAbbonamentoCopyWith(_NumeriAbbonamento value, $Res Function(_NumeriAbbonamento) _then) = __$NumeriAbbonamentoCopyWithImpl;
@override @useResult
$Res call({
 num scontoRinnovo, num scontoProva, int giorniProva, int giorniTolleranza
});




}
/// @nodoc
class __$NumeriAbbonamentoCopyWithImpl<$Res>
    implements _$NumeriAbbonamentoCopyWith<$Res> {
  __$NumeriAbbonamentoCopyWithImpl(this._self, this._then);

  final _NumeriAbbonamento _self;
  final $Res Function(_NumeriAbbonamento) _then;

/// Create a copy of NumeriAbbonamento
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? scontoRinnovo = null,Object? scontoProva = null,Object? giorniProva = null,Object? giorniTolleranza = null,}) {
  return _then(_NumeriAbbonamento(
scontoRinnovo: null == scontoRinnovo ? _self.scontoRinnovo : scontoRinnovo // ignore: cast_nullable_to_non_nullable
as num,scontoProva: null == scontoProva ? _self.scontoProva : scontoProva // ignore: cast_nullable_to_non_nullable
as num,giorniProva: null == giorniProva ? _self.giorniProva : giorniProva // ignore: cast_nullable_to_non_nullable
as int,giorniTolleranza: null == giorniTolleranza ? _self.giorniTolleranza : giorniTolleranza // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$MioAbbonamento {

 AbbonamentoDettaglio? get abbonamento; IdoneitaProva get prova; NumeriAbbonamento get impostazioni; int get saldo;
/// Create a copy of MioAbbonamento
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MioAbbonamentoCopyWith<MioAbbonamento> get copyWith => _$MioAbbonamentoCopyWithImpl<MioAbbonamento>(this as MioAbbonamento, _$identity);

  /// Serializes this MioAbbonamento to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as MioAbbonamento;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is MioAbbonamento&&(identical(other.abbonamento, _this.abbonamento) || other.abbonamento == _this.abbonamento)&&(identical(other.prova, _this.prova) || other.prova == _this.prova)&&(identical(other.impostazioni, _this.impostazioni) || other.impostazioni == _this.impostazioni)&&(identical(other.saldo, _this.saldo) || other.saldo == _this.saldo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as MioAbbonamento;
  return Object.hash(runtimeType,_this.abbonamento,_this.prova,_this.impostazioni,_this.saldo);
}

@override
String toString() {
  final _this = this as MioAbbonamento;
  return 'MioAbbonamento(abbonamento: ${_this.abbonamento}, prova: ${_this.prova}, impostazioni: ${_this.impostazioni}, saldo: ${_this.saldo})';
}


}

/// @nodoc
abstract mixin class $MioAbbonamentoCopyWith<$Res>  {
  factory $MioAbbonamentoCopyWith(MioAbbonamento value, $Res Function(MioAbbonamento) _then) = _$MioAbbonamentoCopyWithImpl;
@useResult
$Res call({
 AbbonamentoDettaglio? abbonamento, IdoneitaProva prova, NumeriAbbonamento impostazioni, int saldo
});


$AbbonamentoDettaglioCopyWith<$Res>? get abbonamento;$IdoneitaProvaCopyWith<$Res> get prova;$NumeriAbbonamentoCopyWith<$Res> get impostazioni;

}
/// @nodoc
class _$MioAbbonamentoCopyWithImpl<$Res>
    implements $MioAbbonamentoCopyWith<$Res> {
  _$MioAbbonamentoCopyWithImpl(this._self, this._then);

  final MioAbbonamento _self;
  final $Res Function(MioAbbonamento) _then;

/// Create a copy of MioAbbonamento
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? abbonamento = freezed,Object? prova = null,Object? impostazioni = null,Object? saldo = null,}) {
  return _then(MioAbbonamento(
abbonamento: freezed == abbonamento ? _self.abbonamento : abbonamento // ignore: cast_nullable_to_non_nullable
as AbbonamentoDettaglio?,prova: null == prova ? _self.prova : prova // ignore: cast_nullable_to_non_nullable
as IdoneitaProva,impostazioni: null == impostazioni ? _self.impostazioni : impostazioni // ignore: cast_nullable_to_non_nullable
as NumeriAbbonamento,saldo: null == saldo ? _self.saldo : saldo // ignore: cast_nullable_to_non_nullable
as int,
  ));
}
/// Create a copy of MioAbbonamento
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$AbbonamentoDettaglioCopyWith<$Res>? get abbonamento {
    if (_self.abbonamento == null) {
    return null;
  }

  return $AbbonamentoDettaglioCopyWith<$Res>(_self.abbonamento!, (value) {
    return _then(_self.copyWith(abbonamento: value));
  });
}/// Create a copy of MioAbbonamento
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$IdoneitaProvaCopyWith<$Res> get prova {
  
  return $IdoneitaProvaCopyWith<$Res>(_self.prova, (value) {
    return _then(_self.copyWith(prova: value));
  });
}/// Create a copy of MioAbbonamento
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$NumeriAbbonamentoCopyWith<$Res> get impostazioni {
  
  return $NumeriAbbonamentoCopyWith<$Res>(_self.impostazioni, (value) {
    return _then(_self.copyWith(impostazioni: value));
  });
}
}


/// Adds pattern-matching-related methods to [MioAbbonamento].
extension MioAbbonamentoPatterns on MioAbbonamento {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MioAbbonamento value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MioAbbonamento() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MioAbbonamento value)  $default,){
final _that = this;
switch (_that) {
case _MioAbbonamento():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MioAbbonamento value)?  $default,){
final _that = this;
switch (_that) {
case _MioAbbonamento() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( AbbonamentoDettaglio? abbonamento,  IdoneitaProva prova,  NumeriAbbonamento impostazioni,  int saldo)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MioAbbonamento() when $default != null:
return $default(_that.abbonamento,_that.prova,_that.impostazioni,_that.saldo);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( AbbonamentoDettaglio? abbonamento,  IdoneitaProva prova,  NumeriAbbonamento impostazioni,  int saldo)  $default,) {final _that = this;
switch (_that) {
case _MioAbbonamento():
return $default(_that.abbonamento,_that.prova,_that.impostazioni,_that.saldo);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( AbbonamentoDettaglio? abbonamento,  IdoneitaProva prova,  NumeriAbbonamento impostazioni,  int saldo)?  $default,) {final _that = this;
switch (_that) {
case _MioAbbonamento() when $default != null:
return $default(_that.abbonamento,_that.prova,_that.impostazioni,_that.saldo);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _MioAbbonamento implements MioAbbonamento {
  const _MioAbbonamento({this.abbonamento, required this.prova, this.impostazioni = const NumeriAbbonamento(), this.saldo = 0});
  factory _MioAbbonamento.fromJson(Map<String, dynamic> json) => _$MioAbbonamentoFromJson(json);

@override final  AbbonamentoDettaglio? abbonamento;
@override final  IdoneitaProva prova;
@override@JsonKey() final  NumeriAbbonamento impostazioni;
@override@JsonKey() final  int saldo;

/// Create a copy of MioAbbonamento
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MioAbbonamentoCopyWith<_MioAbbonamento> get copyWith => __$MioAbbonamentoCopyWithImpl<_MioAbbonamento>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MioAbbonamentoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _MioAbbonamento&&(identical(other.abbonamento, abbonamento) || other.abbonamento == abbonamento)&&(identical(other.prova, prova) || other.prova == prova)&&(identical(other.impostazioni, impostazioni) || other.impostazioni == impostazioni)&&(identical(other.saldo, saldo) || other.saldo == saldo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,abbonamento,prova,impostazioni,saldo);
}

@override
String toString() {
    return 'MioAbbonamento(abbonamento: $abbonamento, prova: $prova, impostazioni: $impostazioni, saldo: $saldo)';
}


}

/// @nodoc
abstract mixin class _$MioAbbonamentoCopyWith<$Res> implements $MioAbbonamentoCopyWith<$Res> {
  factory _$MioAbbonamentoCopyWith(_MioAbbonamento value, $Res Function(_MioAbbonamento) _then) = __$MioAbbonamentoCopyWithImpl;
@override @useResult
$Res call({
 AbbonamentoDettaglio? abbonamento, IdoneitaProva prova, NumeriAbbonamento impostazioni, int saldo
});


@override $AbbonamentoDettaglioCopyWith<$Res>? get abbonamento;@override $IdoneitaProvaCopyWith<$Res> get prova;@override $NumeriAbbonamentoCopyWith<$Res> get impostazioni;

}
/// @nodoc
class __$MioAbbonamentoCopyWithImpl<$Res>
    implements _$MioAbbonamentoCopyWith<$Res> {
  __$MioAbbonamentoCopyWithImpl(this._self, this._then);

  final _MioAbbonamento _self;
  final $Res Function(_MioAbbonamento) _then;

/// Create a copy of MioAbbonamento
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? abbonamento = freezed,Object? prova = null,Object? impostazioni = null,Object? saldo = null,}) {
  return _then(_MioAbbonamento(
abbonamento: freezed == abbonamento ? _self.abbonamento : abbonamento // ignore: cast_nullable_to_non_nullable
as AbbonamentoDettaglio?,prova: null == prova ? _self.prova : prova // ignore: cast_nullable_to_non_nullable
as IdoneitaProva,impostazioni: null == impostazioni ? _self.impostazioni : impostazioni // ignore: cast_nullable_to_non_nullable
as NumeriAbbonamento,saldo: null == saldo ? _self.saldo : saldo // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

/// Create a copy of MioAbbonamento
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$AbbonamentoDettaglioCopyWith<$Res>? get abbonamento {
    if (_self.abbonamento == null) {
    return null;
  }

  return $AbbonamentoDettaglioCopyWith<$Res>(_self.abbonamento!, (value) {
    return _then(_self.copyWith(abbonamento: value));
  });
}/// Create a copy of MioAbbonamento
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$IdoneitaProvaCopyWith<$Res> get prova {
  
  return $IdoneitaProvaCopyWith<$Res>(_self.prova, (value) {
    return _then(_self.copyWith(prova: value));
  });
}/// Create a copy of MioAbbonamento
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$NumeriAbbonamentoCopyWith<$Res> get impostazioni {
  
  return $NumeriAbbonamentoCopyWith<$Res>(_self.impostazioni, (value) {
    return _then(_self.copyWith(impostazioni: value));
  });
}
}


/// @nodoc
mixin _$Conguaglio {

/// `upgrade` o `downgrade`.
 String get tipo; String get piano; String get nome; bool get annuale; bool get rinnovo; int get listino; num get scontoRinnovo; int get nuovo; int get residuo; int get totale; int get pagato; int get giorniRimasti; int get giorniPeriodo; String get decorre; String get valuta;
/// Create a copy of Conguaglio
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ConguaglioCopyWith<Conguaglio> get copyWith => _$ConguaglioCopyWithImpl<Conguaglio>(this as Conguaglio, _$identity);

  /// Serializes this Conguaglio to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Conguaglio;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Conguaglio&&(identical(other.tipo, _this.tipo) || other.tipo == _this.tipo)&&(identical(other.piano, _this.piano) || other.piano == _this.piano)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.annuale, _this.annuale) || other.annuale == _this.annuale)&&(identical(other.rinnovo, _this.rinnovo) || other.rinnovo == _this.rinnovo)&&(identical(other.listino, _this.listino) || other.listino == _this.listino)&&(identical(other.scontoRinnovo, _this.scontoRinnovo) || other.scontoRinnovo == _this.scontoRinnovo)&&(identical(other.nuovo, _this.nuovo) || other.nuovo == _this.nuovo)&&(identical(other.residuo, _this.residuo) || other.residuo == _this.residuo)&&(identical(other.totale, _this.totale) || other.totale == _this.totale)&&(identical(other.pagato, _this.pagato) || other.pagato == _this.pagato)&&(identical(other.giorniRimasti, _this.giorniRimasti) || other.giorniRimasti == _this.giorniRimasti)&&(identical(other.giorniPeriodo, _this.giorniPeriodo) || other.giorniPeriodo == _this.giorniPeriodo)&&(identical(other.decorre, _this.decorre) || other.decorre == _this.decorre)&&(identical(other.valuta, _this.valuta) || other.valuta == _this.valuta));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Conguaglio;
  return Object.hash(runtimeType,_this.tipo,_this.piano,_this.nome,_this.annuale,_this.rinnovo,_this.listino,_this.scontoRinnovo,_this.nuovo,_this.residuo,_this.totale,_this.pagato,_this.giorniRimasti,_this.giorniPeriodo,_this.decorre,_this.valuta);
}

@override
String toString() {
  final _this = this as Conguaglio;
  return 'Conguaglio(tipo: ${_this.tipo}, piano: ${_this.piano}, nome: ${_this.nome}, annuale: ${_this.annuale}, rinnovo: ${_this.rinnovo}, listino: ${_this.listino}, scontoRinnovo: ${_this.scontoRinnovo}, nuovo: ${_this.nuovo}, residuo: ${_this.residuo}, totale: ${_this.totale}, pagato: ${_this.pagato}, giorniRimasti: ${_this.giorniRimasti}, giorniPeriodo: ${_this.giorniPeriodo}, decorre: ${_this.decorre}, valuta: ${_this.valuta})';
}


}

/// @nodoc
abstract mixin class $ConguaglioCopyWith<$Res>  {
  factory $ConguaglioCopyWith(Conguaglio value, $Res Function(Conguaglio) _then) = _$ConguaglioCopyWithImpl;
@useResult
$Res call({
 String tipo, String piano, String nome, bool annuale, bool rinnovo, int listino, num scontoRinnovo, int nuovo, int residuo, int totale, int pagato, int giorniRimasti, int giorniPeriodo, String decorre, String valuta
});




}
/// @nodoc
class _$ConguaglioCopyWithImpl<$Res>
    implements $ConguaglioCopyWith<$Res> {
  _$ConguaglioCopyWithImpl(this._self, this._then);

  final Conguaglio _self;
  final $Res Function(Conguaglio) _then;

/// Create a copy of Conguaglio
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? tipo = null,Object? piano = null,Object? nome = null,Object? annuale = null,Object? rinnovo = null,Object? listino = null,Object? scontoRinnovo = null,Object? nuovo = null,Object? residuo = null,Object? totale = null,Object? pagato = null,Object? giorniRimasti = null,Object? giorniPeriodo = null,Object? decorre = null,Object? valuta = null,}) {
  return _then(Conguaglio(
tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,piano: null == piano ? _self.piano : piano // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,annuale: null == annuale ? _self.annuale : annuale // ignore: cast_nullable_to_non_nullable
as bool,rinnovo: null == rinnovo ? _self.rinnovo : rinnovo // ignore: cast_nullable_to_non_nullable
as bool,listino: null == listino ? _self.listino : listino // ignore: cast_nullable_to_non_nullable
as int,scontoRinnovo: null == scontoRinnovo ? _self.scontoRinnovo : scontoRinnovo // ignore: cast_nullable_to_non_nullable
as num,nuovo: null == nuovo ? _self.nuovo : nuovo // ignore: cast_nullable_to_non_nullable
as int,residuo: null == residuo ? _self.residuo : residuo // ignore: cast_nullable_to_non_nullable
as int,totale: null == totale ? _self.totale : totale // ignore: cast_nullable_to_non_nullable
as int,pagato: null == pagato ? _self.pagato : pagato // ignore: cast_nullable_to_non_nullable
as int,giorniRimasti: null == giorniRimasti ? _self.giorniRimasti : giorniRimasti // ignore: cast_nullable_to_non_nullable
as int,giorniPeriodo: null == giorniPeriodo ? _self.giorniPeriodo : giorniPeriodo // ignore: cast_nullable_to_non_nullable
as int,decorre: null == decorre ? _self.decorre : decorre // ignore: cast_nullable_to_non_nullable
as String,valuta: null == valuta ? _self.valuta : valuta // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [Conguaglio].
extension ConguaglioPatterns on Conguaglio {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Conguaglio value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Conguaglio() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Conguaglio value)  $default,){
final _that = this;
switch (_that) {
case _Conguaglio():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Conguaglio value)?  $default,){
final _that = this;
switch (_that) {
case _Conguaglio() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String tipo,  String piano,  String nome,  bool annuale,  bool rinnovo,  int listino,  num scontoRinnovo,  int nuovo,  int residuo,  int totale,  int pagato,  int giorniRimasti,  int giorniPeriodo,  String decorre,  String valuta)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Conguaglio() when $default != null:
return $default(_that.tipo,_that.piano,_that.nome,_that.annuale,_that.rinnovo,_that.listino,_that.scontoRinnovo,_that.nuovo,_that.residuo,_that.totale,_that.pagato,_that.giorniRimasti,_that.giorniPeriodo,_that.decorre,_that.valuta);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String tipo,  String piano,  String nome,  bool annuale,  bool rinnovo,  int listino,  num scontoRinnovo,  int nuovo,  int residuo,  int totale,  int pagato,  int giorniRimasti,  int giorniPeriodo,  String decorre,  String valuta)  $default,) {final _that = this;
switch (_that) {
case _Conguaglio():
return $default(_that.tipo,_that.piano,_that.nome,_that.annuale,_that.rinnovo,_that.listino,_that.scontoRinnovo,_that.nuovo,_that.residuo,_that.totale,_that.pagato,_that.giorniRimasti,_that.giorniPeriodo,_that.decorre,_that.valuta);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String tipo,  String piano,  String nome,  bool annuale,  bool rinnovo,  int listino,  num scontoRinnovo,  int nuovo,  int residuo,  int totale,  int pagato,  int giorniRimasti,  int giorniPeriodo,  String decorre,  String valuta)?  $default,) {final _that = this;
switch (_that) {
case _Conguaglio() when $default != null:
return $default(_that.tipo,_that.piano,_that.nome,_that.annuale,_that.rinnovo,_that.listino,_that.scontoRinnovo,_that.nuovo,_that.residuo,_that.totale,_that.pagato,_that.giorniRimasti,_that.giorniPeriodo,_that.decorre,_that.valuta);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Conguaglio implements Conguaglio {
  const _Conguaglio({required this.tipo, required this.piano, required this.nome, this.annuale = false, this.rinnovo = false, this.listino = 0, this.scontoRinnovo = 0, this.nuovo = 0, this.residuo = 0, this.totale = 0, this.pagato = 0, this.giorniRimasti = 0, this.giorniPeriodo = 0, required this.decorre, this.valuta = 'EUR'});
  factory _Conguaglio.fromJson(Map<String, dynamic> json) => _$ConguaglioFromJson(json);

/// `upgrade` o `downgrade`.
@override final  String tipo;
@override final  String piano;
@override final  String nome;
@override@JsonKey() final  bool annuale;
@override@JsonKey() final  bool rinnovo;
@override@JsonKey() final  int listino;
@override@JsonKey() final  num scontoRinnovo;
@override@JsonKey() final  int nuovo;
@override@JsonKey() final  int residuo;
@override@JsonKey() final  int totale;
@override@JsonKey() final  int pagato;
@override@JsonKey() final  int giorniRimasti;
@override@JsonKey() final  int giorniPeriodo;
@override final  String decorre;
@override@JsonKey() final  String valuta;

/// Create a copy of Conguaglio
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ConguaglioCopyWith<_Conguaglio> get copyWith => __$ConguaglioCopyWithImpl<_Conguaglio>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ConguaglioToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Conguaglio&&(identical(other.tipo, tipo) || other.tipo == tipo)&&(identical(other.piano, piano) || other.piano == piano)&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.annuale, annuale) || other.annuale == annuale)&&(identical(other.rinnovo, rinnovo) || other.rinnovo == rinnovo)&&(identical(other.listino, listino) || other.listino == listino)&&(identical(other.scontoRinnovo, scontoRinnovo) || other.scontoRinnovo == scontoRinnovo)&&(identical(other.nuovo, nuovo) || other.nuovo == nuovo)&&(identical(other.residuo, residuo) || other.residuo == residuo)&&(identical(other.totale, totale) || other.totale == totale)&&(identical(other.pagato, pagato) || other.pagato == pagato)&&(identical(other.giorniRimasti, giorniRimasti) || other.giorniRimasti == giorniRimasti)&&(identical(other.giorniPeriodo, giorniPeriodo) || other.giorniPeriodo == giorniPeriodo)&&(identical(other.decorre, decorre) || other.decorre == decorre)&&(identical(other.valuta, valuta) || other.valuta == valuta));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,tipo,piano,nome,annuale,rinnovo,listino,scontoRinnovo,nuovo,residuo,totale,pagato,giorniRimasti,giorniPeriodo,decorre,valuta);
}

@override
String toString() {
    return 'Conguaglio(tipo: $tipo, piano: $piano, nome: $nome, annuale: $annuale, rinnovo: $rinnovo, listino: $listino, scontoRinnovo: $scontoRinnovo, nuovo: $nuovo, residuo: $residuo, totale: $totale, pagato: $pagato, giorniRimasti: $giorniRimasti, giorniPeriodo: $giorniPeriodo, decorre: $decorre, valuta: $valuta)';
}


}

/// @nodoc
abstract mixin class _$ConguaglioCopyWith<$Res> implements $ConguaglioCopyWith<$Res> {
  factory _$ConguaglioCopyWith(_Conguaglio value, $Res Function(_Conguaglio) _then) = __$ConguaglioCopyWithImpl;
@override @useResult
$Res call({
 String tipo, String piano, String nome, bool annuale, bool rinnovo, int listino, num scontoRinnovo, int nuovo, int residuo, int totale, int pagato, int giorniRimasti, int giorniPeriodo, String decorre, String valuta
});




}
/// @nodoc
class __$ConguaglioCopyWithImpl<$Res>
    implements _$ConguaglioCopyWith<$Res> {
  __$ConguaglioCopyWithImpl(this._self, this._then);

  final _Conguaglio _self;
  final $Res Function(_Conguaglio) _then;

/// Create a copy of Conguaglio
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? tipo = null,Object? piano = null,Object? nome = null,Object? annuale = null,Object? rinnovo = null,Object? listino = null,Object? scontoRinnovo = null,Object? nuovo = null,Object? residuo = null,Object? totale = null,Object? pagato = null,Object? giorniRimasti = null,Object? giorniPeriodo = null,Object? decorre = null,Object? valuta = null,}) {
  return _then(_Conguaglio(
tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,piano: null == piano ? _self.piano : piano // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,annuale: null == annuale ? _self.annuale : annuale // ignore: cast_nullable_to_non_nullable
as bool,rinnovo: null == rinnovo ? _self.rinnovo : rinnovo // ignore: cast_nullable_to_non_nullable
as bool,listino: null == listino ? _self.listino : listino // ignore: cast_nullable_to_non_nullable
as int,scontoRinnovo: null == scontoRinnovo ? _self.scontoRinnovo : scontoRinnovo // ignore: cast_nullable_to_non_nullable
as num,nuovo: null == nuovo ? _self.nuovo : nuovo // ignore: cast_nullable_to_non_nullable
as int,residuo: null == residuo ? _self.residuo : residuo // ignore: cast_nullable_to_non_nullable
as int,totale: null == totale ? _self.totale : totale // ignore: cast_nullable_to_non_nullable
as int,pagato: null == pagato ? _self.pagato : pagato // ignore: cast_nullable_to_non_nullable
as int,giorniRimasti: null == giorniRimasti ? _self.giorniRimasti : giorniRimasti // ignore: cast_nullable_to_non_nullable
as int,giorniPeriodo: null == giorniPeriodo ? _self.giorniPeriodo : giorniPeriodo // ignore: cast_nullable_to_non_nullable
as int,decorre: null == decorre ? _self.decorre : decorre // ignore: cast_nullable_to_non_nullable
as String,valuta: null == valuta ? _self.valuta : valuta // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$EsitoCambio {

 String get tipo; Conguaglio get conguaglio; String? get url; int? get importo; AbbonamentoDettaglio? get abbonamento;
/// Create a copy of EsitoCambio
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$EsitoCambioCopyWith<EsitoCambio> get copyWith => _$EsitoCambioCopyWithImpl<EsitoCambio>(this as EsitoCambio, _$identity);

  /// Serializes this EsitoCambio to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as EsitoCambio;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is EsitoCambio&&(identical(other.tipo, _this.tipo) || other.tipo == _this.tipo)&&(identical(other.conguaglio, _this.conguaglio) || other.conguaglio == _this.conguaglio)&&(identical(other.url, _this.url) || other.url == _this.url)&&(identical(other.importo, _this.importo) || other.importo == _this.importo)&&(identical(other.abbonamento, _this.abbonamento) || other.abbonamento == _this.abbonamento));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as EsitoCambio;
  return Object.hash(runtimeType,_this.tipo,_this.conguaglio,_this.url,_this.importo,_this.abbonamento);
}

@override
String toString() {
  final _this = this as EsitoCambio;
  return 'EsitoCambio(tipo: ${_this.tipo}, conguaglio: ${_this.conguaglio}, url: ${_this.url}, importo: ${_this.importo}, abbonamento: ${_this.abbonamento})';
}


}

/// @nodoc
abstract mixin class $EsitoCambioCopyWith<$Res>  {
  factory $EsitoCambioCopyWith(EsitoCambio value, $Res Function(EsitoCambio) _then) = _$EsitoCambioCopyWithImpl;
@useResult
$Res call({
 String tipo, Conguaglio conguaglio, String? url, int? importo, AbbonamentoDettaglio? abbonamento
});


$ConguaglioCopyWith<$Res> get conguaglio;$AbbonamentoDettaglioCopyWith<$Res>? get abbonamento;

}
/// @nodoc
class _$EsitoCambioCopyWithImpl<$Res>
    implements $EsitoCambioCopyWith<$Res> {
  _$EsitoCambioCopyWithImpl(this._self, this._then);

  final EsitoCambio _self;
  final $Res Function(EsitoCambio) _then;

/// Create a copy of EsitoCambio
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? tipo = null,Object? conguaglio = null,Object? url = freezed,Object? importo = freezed,Object? abbonamento = freezed,}) {
  return _then(EsitoCambio(
tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,conguaglio: null == conguaglio ? _self.conguaglio : conguaglio // ignore: cast_nullable_to_non_nullable
as Conguaglio,url: freezed == url ? _self.url : url // ignore: cast_nullable_to_non_nullable
as String?,importo: freezed == importo ? _self.importo : importo // ignore: cast_nullable_to_non_nullable
as int?,abbonamento: freezed == abbonamento ? _self.abbonamento : abbonamento // ignore: cast_nullable_to_non_nullable
as AbbonamentoDettaglio?,
  ));
}
/// Create a copy of EsitoCambio
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ConguaglioCopyWith<$Res> get conguaglio {
  
  return $ConguaglioCopyWith<$Res>(_self.conguaglio, (value) {
    return _then(_self.copyWith(conguaglio: value));
  });
}/// Create a copy of EsitoCambio
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$AbbonamentoDettaglioCopyWith<$Res>? get abbonamento {
    if (_self.abbonamento == null) {
    return null;
  }

  return $AbbonamentoDettaglioCopyWith<$Res>(_self.abbonamento!, (value) {
    return _then(_self.copyWith(abbonamento: value));
  });
}
}


/// Adds pattern-matching-related methods to [EsitoCambio].
extension EsitoCambioPatterns on EsitoCambio {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _EsitoCambio value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _EsitoCambio() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _EsitoCambio value)  $default,){
final _that = this;
switch (_that) {
case _EsitoCambio():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _EsitoCambio value)?  $default,){
final _that = this;
switch (_that) {
case _EsitoCambio() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String tipo,  Conguaglio conguaglio,  String? url,  int? importo,  AbbonamentoDettaglio? abbonamento)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _EsitoCambio() when $default != null:
return $default(_that.tipo,_that.conguaglio,_that.url,_that.importo,_that.abbonamento);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String tipo,  Conguaglio conguaglio,  String? url,  int? importo,  AbbonamentoDettaglio? abbonamento)  $default,) {final _that = this;
switch (_that) {
case _EsitoCambio():
return $default(_that.tipo,_that.conguaglio,_that.url,_that.importo,_that.abbonamento);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String tipo,  Conguaglio conguaglio,  String? url,  int? importo,  AbbonamentoDettaglio? abbonamento)?  $default,) {final _that = this;
switch (_that) {
case _EsitoCambio() when $default != null:
return $default(_that.tipo,_that.conguaglio,_that.url,_that.importo,_that.abbonamento);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _EsitoCambio implements EsitoCambio {
  const _EsitoCambio({required this.tipo, required this.conguaglio, this.url, this.importo, this.abbonamento});
  factory _EsitoCambio.fromJson(Map<String, dynamic> json) => _$EsitoCambioFromJson(json);

@override final  String tipo;
@override final  Conguaglio conguaglio;
@override final  String? url;
@override final  int? importo;
@override final  AbbonamentoDettaglio? abbonamento;

/// Create a copy of EsitoCambio
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$EsitoCambioCopyWith<_EsitoCambio> get copyWith => __$EsitoCambioCopyWithImpl<_EsitoCambio>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$EsitoCambioToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _EsitoCambio&&(identical(other.tipo, tipo) || other.tipo == tipo)&&(identical(other.conguaglio, conguaglio) || other.conguaglio == conguaglio)&&(identical(other.url, url) || other.url == url)&&(identical(other.importo, importo) || other.importo == importo)&&(identical(other.abbonamento, abbonamento) || other.abbonamento == abbonamento));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,tipo,conguaglio,url,importo,abbonamento);
}

@override
String toString() {
    return 'EsitoCambio(tipo: $tipo, conguaglio: $conguaglio, url: $url, importo: $importo, abbonamento: $abbonamento)';
}


}

/// @nodoc
abstract mixin class _$EsitoCambioCopyWith<$Res> implements $EsitoCambioCopyWith<$Res> {
  factory _$EsitoCambioCopyWith(_EsitoCambio value, $Res Function(_EsitoCambio) _then) = __$EsitoCambioCopyWithImpl;
@override @useResult
$Res call({
 String tipo, Conguaglio conguaglio, String? url, int? importo, AbbonamentoDettaglio? abbonamento
});


@override $ConguaglioCopyWith<$Res> get conguaglio;@override $AbbonamentoDettaglioCopyWith<$Res>? get abbonamento;

}
/// @nodoc
class __$EsitoCambioCopyWithImpl<$Res>
    implements _$EsitoCambioCopyWith<$Res> {
  __$EsitoCambioCopyWithImpl(this._self, this._then);

  final _EsitoCambio _self;
  final $Res Function(_EsitoCambio) _then;

/// Create a copy of EsitoCambio
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? tipo = null,Object? conguaglio = null,Object? url = freezed,Object? importo = freezed,Object? abbonamento = freezed,}) {
  return _then(_EsitoCambio(
tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,conguaglio: null == conguaglio ? _self.conguaglio : conguaglio // ignore: cast_nullable_to_non_nullable
as Conguaglio,url: freezed == url ? _self.url : url // ignore: cast_nullable_to_non_nullable
as String?,importo: freezed == importo ? _self.importo : importo // ignore: cast_nullable_to_non_nullable
as int?,abbonamento: freezed == abbonamento ? _self.abbonamento : abbonamento // ignore: cast_nullable_to_non_nullable
as AbbonamentoDettaglio?,
  ));
}

/// Create a copy of EsitoCambio
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ConguaglioCopyWith<$Res> get conguaglio {
  
  return $ConguaglioCopyWith<$Res>(_self.conguaglio, (value) {
    return _then(_self.copyWith(conguaglio: value));
  });
}/// Create a copy of EsitoCambio
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$AbbonamentoDettaglioCopyWith<$Res>? get abbonamento {
    if (_self.abbonamento == null) {
    return null;
  }

  return $AbbonamentoDettaglioCopyWith<$Res>(_self.abbonamento!, (value) {
    return _then(_self.copyWith(abbonamento: value));
  });
}
}


/// @nodoc
mixin _$PagamentoDaSistemare {

 String get provider; bool get store; String? get url; bool get giaPagata;
/// Create a copy of PagamentoDaSistemare
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PagamentoDaSistemareCopyWith<PagamentoDaSistemare> get copyWith => _$PagamentoDaSistemareCopyWithImpl<PagamentoDaSistemare>(this as PagamentoDaSistemare, _$identity);

  /// Serializes this PagamentoDaSistemare to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as PagamentoDaSistemare;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PagamentoDaSistemare&&(identical(other.provider, _this.provider) || other.provider == _this.provider)&&(identical(other.store, _this.store) || other.store == _this.store)&&(identical(other.url, _this.url) || other.url == _this.url)&&(identical(other.giaPagata, _this.giaPagata) || other.giaPagata == _this.giaPagata));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as PagamentoDaSistemare;
  return Object.hash(runtimeType,_this.provider,_this.store,_this.url,_this.giaPagata);
}

@override
String toString() {
  final _this = this as PagamentoDaSistemare;
  return 'PagamentoDaSistemare(provider: ${_this.provider}, store: ${_this.store}, url: ${_this.url}, giaPagata: ${_this.giaPagata})';
}


}

/// @nodoc
abstract mixin class $PagamentoDaSistemareCopyWith<$Res>  {
  factory $PagamentoDaSistemareCopyWith(PagamentoDaSistemare value, $Res Function(PagamentoDaSistemare) _then) = _$PagamentoDaSistemareCopyWithImpl;
@useResult
$Res call({
 String provider, bool store, String? url, bool giaPagata
});




}
/// @nodoc
class _$PagamentoDaSistemareCopyWithImpl<$Res>
    implements $PagamentoDaSistemareCopyWith<$Res> {
  _$PagamentoDaSistemareCopyWithImpl(this._self, this._then);

  final PagamentoDaSistemare _self;
  final $Res Function(PagamentoDaSistemare) _then;

/// Create a copy of PagamentoDaSistemare
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? provider = null,Object? store = null,Object? url = freezed,Object? giaPagata = null,}) {
  return _then(PagamentoDaSistemare(
provider: null == provider ? _self.provider : provider // ignore: cast_nullable_to_non_nullable
as String,store: null == store ? _self.store : store // ignore: cast_nullable_to_non_nullable
as bool,url: freezed == url ? _self.url : url // ignore: cast_nullable_to_non_nullable
as String?,giaPagata: null == giaPagata ? _self.giaPagata : giaPagata // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [PagamentoDaSistemare].
extension PagamentoDaSistemarePatterns on PagamentoDaSistemare {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PagamentoDaSistemare value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PagamentoDaSistemare() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PagamentoDaSistemare value)  $default,){
final _that = this;
switch (_that) {
case _PagamentoDaSistemare():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PagamentoDaSistemare value)?  $default,){
final _that = this;
switch (_that) {
case _PagamentoDaSistemare() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String provider,  bool store,  String? url,  bool giaPagata)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PagamentoDaSistemare() when $default != null:
return $default(_that.provider,_that.store,_that.url,_that.giaPagata);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String provider,  bool store,  String? url,  bool giaPagata)  $default,) {final _that = this;
switch (_that) {
case _PagamentoDaSistemare():
return $default(_that.provider,_that.store,_that.url,_that.giaPagata);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String provider,  bool store,  String? url,  bool giaPagata)?  $default,) {final _that = this;
switch (_that) {
case _PagamentoDaSistemare() when $default != null:
return $default(_that.provider,_that.store,_that.url,_that.giaPagata);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _PagamentoDaSistemare implements PagamentoDaSistemare {
  const _PagamentoDaSistemare({required this.provider, this.store = false, this.url, this.giaPagata = false});
  factory _PagamentoDaSistemare.fromJson(Map<String, dynamic> json) => _$PagamentoDaSistemareFromJson(json);

@override final  String provider;
@override@JsonKey() final  bool store;
@override final  String? url;
@override@JsonKey() final  bool giaPagata;

/// Create a copy of PagamentoDaSistemare
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PagamentoDaSistemareCopyWith<_PagamentoDaSistemare> get copyWith => __$PagamentoDaSistemareCopyWithImpl<_PagamentoDaSistemare>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PagamentoDaSistemareToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _PagamentoDaSistemare&&(identical(other.provider, provider) || other.provider == provider)&&(identical(other.store, store) || other.store == store)&&(identical(other.url, url) || other.url == url)&&(identical(other.giaPagata, giaPagata) || other.giaPagata == giaPagata));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,provider,store,url,giaPagata);
}

@override
String toString() {
    return 'PagamentoDaSistemare(provider: $provider, store: $store, url: $url, giaPagata: $giaPagata)';
}


}

/// @nodoc
abstract mixin class _$PagamentoDaSistemareCopyWith<$Res> implements $PagamentoDaSistemareCopyWith<$Res> {
  factory _$PagamentoDaSistemareCopyWith(_PagamentoDaSistemare value, $Res Function(_PagamentoDaSistemare) _then) = __$PagamentoDaSistemareCopyWithImpl;
@override @useResult
$Res call({
 String provider, bool store, String? url, bool giaPagata
});




}
/// @nodoc
class __$PagamentoDaSistemareCopyWithImpl<$Res>
    implements _$PagamentoDaSistemareCopyWith<$Res> {
  __$PagamentoDaSistemareCopyWithImpl(this._self, this._then);

  final _PagamentoDaSistemare _self;
  final $Res Function(_PagamentoDaSistemare) _then;

/// Create a copy of PagamentoDaSistemare
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? provider = null,Object? store = null,Object? url = freezed,Object? giaPagata = null,}) {
  return _then(_PagamentoDaSistemare(
provider: null == provider ? _self.provider : provider // ignore: cast_nullable_to_non_nullable
as String,store: null == store ? _self.store : store // ignore: cast_nullable_to_non_nullable
as bool,url: freezed == url ? _self.url : url // ignore: cast_nullable_to_non_nullable
as String?,giaPagata: null == giaPagata ? _self.giaPagata : giaPagata // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}


/// @nodoc
mixin _$LimiteSuperato {

/// `letture_al_giorno`, `letture_alla_settimana`, `letture_al_mese`, `letture_totali`.
 String get limite; int get valore; int get usate; int get lettureFatte; String? get siLibera; int get condoniRimasti; int get condoniPerPeriodo; int get saldo;/// `condono`, `credito`, `acquisto`.
 String get scelta;
/// Create a copy of LimiteSuperato
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LimiteSuperatoCopyWith<LimiteSuperato> get copyWith => _$LimiteSuperatoCopyWithImpl<LimiteSuperato>(this as LimiteSuperato, _$identity);

  /// Serializes this LimiteSuperato to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as LimiteSuperato;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is LimiteSuperato&&(identical(other.limite, _this.limite) || other.limite == _this.limite)&&(identical(other.valore, _this.valore) || other.valore == _this.valore)&&(identical(other.usate, _this.usate) || other.usate == _this.usate)&&(identical(other.lettureFatte, _this.lettureFatte) || other.lettureFatte == _this.lettureFatte)&&(identical(other.siLibera, _this.siLibera) || other.siLibera == _this.siLibera)&&(identical(other.condoniRimasti, _this.condoniRimasti) || other.condoniRimasti == _this.condoniRimasti)&&(identical(other.condoniPerPeriodo, _this.condoniPerPeriodo) || other.condoniPerPeriodo == _this.condoniPerPeriodo)&&(identical(other.saldo, _this.saldo) || other.saldo == _this.saldo)&&(identical(other.scelta, _this.scelta) || other.scelta == _this.scelta));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as LimiteSuperato;
  return Object.hash(runtimeType,_this.limite,_this.valore,_this.usate,_this.lettureFatte,_this.siLibera,_this.condoniRimasti,_this.condoniPerPeriodo,_this.saldo,_this.scelta);
}

@override
String toString() {
  final _this = this as LimiteSuperato;
  return 'LimiteSuperato(limite: ${_this.limite}, valore: ${_this.valore}, usate: ${_this.usate}, lettureFatte: ${_this.lettureFatte}, siLibera: ${_this.siLibera}, condoniRimasti: ${_this.condoniRimasti}, condoniPerPeriodo: ${_this.condoniPerPeriodo}, saldo: ${_this.saldo}, scelta: ${_this.scelta})';
}


}

/// @nodoc
abstract mixin class $LimiteSuperatoCopyWith<$Res>  {
  factory $LimiteSuperatoCopyWith(LimiteSuperato value, $Res Function(LimiteSuperato) _then) = _$LimiteSuperatoCopyWithImpl;
@useResult
$Res call({
 String limite, int valore, int usate, int lettureFatte, String? siLibera, int condoniRimasti, int condoniPerPeriodo, int saldo, String scelta
});




}
/// @nodoc
class _$LimiteSuperatoCopyWithImpl<$Res>
    implements $LimiteSuperatoCopyWith<$Res> {
  _$LimiteSuperatoCopyWithImpl(this._self, this._then);

  final LimiteSuperato _self;
  final $Res Function(LimiteSuperato) _then;

/// Create a copy of LimiteSuperato
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? limite = null,Object? valore = null,Object? usate = null,Object? lettureFatte = null,Object? siLibera = freezed,Object? condoniRimasti = null,Object? condoniPerPeriodo = null,Object? saldo = null,Object? scelta = null,}) {
  return _then(LimiteSuperato(
limite: null == limite ? _self.limite : limite // ignore: cast_nullable_to_non_nullable
as String,valore: null == valore ? _self.valore : valore // ignore: cast_nullable_to_non_nullable
as int,usate: null == usate ? _self.usate : usate // ignore: cast_nullable_to_non_nullable
as int,lettureFatte: null == lettureFatte ? _self.lettureFatte : lettureFatte // ignore: cast_nullable_to_non_nullable
as int,siLibera: freezed == siLibera ? _self.siLibera : siLibera // ignore: cast_nullable_to_non_nullable
as String?,condoniRimasti: null == condoniRimasti ? _self.condoniRimasti : condoniRimasti // ignore: cast_nullable_to_non_nullable
as int,condoniPerPeriodo: null == condoniPerPeriodo ? _self.condoniPerPeriodo : condoniPerPeriodo // ignore: cast_nullable_to_non_nullable
as int,saldo: null == saldo ? _self.saldo : saldo // ignore: cast_nullable_to_non_nullable
as int,scelta: null == scelta ? _self.scelta : scelta // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [LimiteSuperato].
extension LimiteSuperatoPatterns on LimiteSuperato {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _LimiteSuperato value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _LimiteSuperato() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _LimiteSuperato value)  $default,){
final _that = this;
switch (_that) {
case _LimiteSuperato():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _LimiteSuperato value)?  $default,){
final _that = this;
switch (_that) {
case _LimiteSuperato() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String limite,  int valore,  int usate,  int lettureFatte,  String? siLibera,  int condoniRimasti,  int condoniPerPeriodo,  int saldo,  String scelta)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _LimiteSuperato() when $default != null:
return $default(_that.limite,_that.valore,_that.usate,_that.lettureFatte,_that.siLibera,_that.condoniRimasti,_that.condoniPerPeriodo,_that.saldo,_that.scelta);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String limite,  int valore,  int usate,  int lettureFatte,  String? siLibera,  int condoniRimasti,  int condoniPerPeriodo,  int saldo,  String scelta)  $default,) {final _that = this;
switch (_that) {
case _LimiteSuperato():
return $default(_that.limite,_that.valore,_that.usate,_that.lettureFatte,_that.siLibera,_that.condoniRimasti,_that.condoniPerPeriodo,_that.saldo,_that.scelta);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String limite,  int valore,  int usate,  int lettureFatte,  String? siLibera,  int condoniRimasti,  int condoniPerPeriodo,  int saldo,  String scelta)?  $default,) {final _that = this;
switch (_that) {
case _LimiteSuperato() when $default != null:
return $default(_that.limite,_that.valore,_that.usate,_that.lettureFatte,_that.siLibera,_that.condoniRimasti,_that.condoniPerPeriodo,_that.saldo,_that.scelta);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _LimiteSuperato implements LimiteSuperato {
  const _LimiteSuperato({required this.limite, this.valore = 0, this.usate = 0, this.lettureFatte = 0, this.siLibera, this.condoniRimasti = 0, this.condoniPerPeriodo = 0, this.saldo = 0, required this.scelta});
  factory _LimiteSuperato.fromJson(Map<String, dynamic> json) => _$LimiteSuperatoFromJson(json);

/// `letture_al_giorno`, `letture_alla_settimana`, `letture_al_mese`, `letture_totali`.
@override final  String limite;
@override@JsonKey() final  int valore;
@override@JsonKey() final  int usate;
@override@JsonKey() final  int lettureFatte;
@override final  String? siLibera;
@override@JsonKey() final  int condoniRimasti;
@override@JsonKey() final  int condoniPerPeriodo;
@override@JsonKey() final  int saldo;
/// `condono`, `credito`, `acquisto`.
@override final  String scelta;

/// Create a copy of LimiteSuperato
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$LimiteSuperatoCopyWith<_LimiteSuperato> get copyWith => __$LimiteSuperatoCopyWithImpl<_LimiteSuperato>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$LimiteSuperatoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _LimiteSuperato&&(identical(other.limite, limite) || other.limite == limite)&&(identical(other.valore, valore) || other.valore == valore)&&(identical(other.usate, usate) || other.usate == usate)&&(identical(other.lettureFatte, lettureFatte) || other.lettureFatte == lettureFatte)&&(identical(other.siLibera, siLibera) || other.siLibera == siLibera)&&(identical(other.condoniRimasti, condoniRimasti) || other.condoniRimasti == condoniRimasti)&&(identical(other.condoniPerPeriodo, condoniPerPeriodo) || other.condoniPerPeriodo == condoniPerPeriodo)&&(identical(other.saldo, saldo) || other.saldo == saldo)&&(identical(other.scelta, scelta) || other.scelta == scelta));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,limite,valore,usate,lettureFatte,siLibera,condoniRimasti,condoniPerPeriodo,saldo,scelta);
}

@override
String toString() {
    return 'LimiteSuperato(limite: $limite, valore: $valore, usate: $usate, lettureFatte: $lettureFatte, siLibera: $siLibera, condoniRimasti: $condoniRimasti, condoniPerPeriodo: $condoniPerPeriodo, saldo: $saldo, scelta: $scelta)';
}


}

/// @nodoc
abstract mixin class _$LimiteSuperatoCopyWith<$Res> implements $LimiteSuperatoCopyWith<$Res> {
  factory _$LimiteSuperatoCopyWith(_LimiteSuperato value, $Res Function(_LimiteSuperato) _then) = __$LimiteSuperatoCopyWithImpl;
@override @useResult
$Res call({
 String limite, int valore, int usate, int lettureFatte, String? siLibera, int condoniRimasti, int condoniPerPeriodo, int saldo, String scelta
});




}
/// @nodoc
class __$LimiteSuperatoCopyWithImpl<$Res>
    implements _$LimiteSuperatoCopyWith<$Res> {
  __$LimiteSuperatoCopyWithImpl(this._self, this._then);

  final _LimiteSuperato _self;
  final $Res Function(_LimiteSuperato) _then;

/// Create a copy of LimiteSuperato
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? limite = null,Object? valore = null,Object? usate = null,Object? lettureFatte = null,Object? siLibera = freezed,Object? condoniRimasti = null,Object? condoniPerPeriodo = null,Object? saldo = null,Object? scelta = null,}) {
  return _then(_LimiteSuperato(
limite: null == limite ? _self.limite : limite // ignore: cast_nullable_to_non_nullable
as String,valore: null == valore ? _self.valore : valore // ignore: cast_nullable_to_non_nullable
as int,usate: null == usate ? _self.usate : usate // ignore: cast_nullable_to_non_nullable
as int,lettureFatte: null == lettureFatte ? _self.lettureFatte : lettureFatte // ignore: cast_nullable_to_non_nullable
as int,siLibera: freezed == siLibera ? _self.siLibera : siLibera // ignore: cast_nullable_to_non_nullable
as String?,condoniRimasti: null == condoniRimasti ? _self.condoniRimasti : condoniRimasti // ignore: cast_nullable_to_non_nullable
as int,condoniPerPeriodo: null == condoniPerPeriodo ? _self.condoniPerPeriodo : condoniPerPeriodo // ignore: cast_nullable_to_non_nullable
as int,saldo: null == saldo ? _self.saldo : saldo // ignore: cast_nullable_to_non_nullable
as int,scelta: null == scelta ? _self.scelta : scelta // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$CouponPubblico {

 String get codice;/// `percentuale` o `importo`.
 String get tipo; num get valore;/// `una_volta`, `periodi`, `sempre`.
 String get durata; int? get periodi; bool get cumulabile; List<String> get piani; String? get validoFino;
/// Create a copy of CouponPubblico
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CouponPubblicoCopyWith<CouponPubblico> get copyWith => _$CouponPubblicoCopyWithImpl<CouponPubblico>(this as CouponPubblico, _$identity);

  /// Serializes this CouponPubblico to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as CouponPubblico;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CouponPubblico&&(identical(other.codice, _this.codice) || other.codice == _this.codice)&&(identical(other.tipo, _this.tipo) || other.tipo == _this.tipo)&&(identical(other.valore, _this.valore) || other.valore == _this.valore)&&(identical(other.durata, _this.durata) || other.durata == _this.durata)&&(identical(other.periodi, _this.periodi) || other.periodi == _this.periodi)&&(identical(other.cumulabile, _this.cumulabile) || other.cumulabile == _this.cumulabile)&&const DeepCollectionEquality().equals(other.piani, _this.piani)&&(identical(other.validoFino, _this.validoFino) || other.validoFino == _this.validoFino));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as CouponPubblico;
  return Object.hash(runtimeType,_this.codice,_this.tipo,_this.valore,_this.durata,_this.periodi,_this.cumulabile,const DeepCollectionEquality().hash(_this.piani),_this.validoFino);
}

@override
String toString() {
  final _this = this as CouponPubblico;
  return 'CouponPubblico(codice: ${_this.codice}, tipo: ${_this.tipo}, valore: ${_this.valore}, durata: ${_this.durata}, periodi: ${_this.periodi}, cumulabile: ${_this.cumulabile}, piani: ${_this.piani}, validoFino: ${_this.validoFino})';
}


}

/// @nodoc
abstract mixin class $CouponPubblicoCopyWith<$Res>  {
  factory $CouponPubblicoCopyWith(CouponPubblico value, $Res Function(CouponPubblico) _then) = _$CouponPubblicoCopyWithImpl;
@useResult
$Res call({
 String codice, String tipo, num valore, String durata, int? periodi, bool cumulabile, List<String> piani, String? validoFino
});




}
/// @nodoc
class _$CouponPubblicoCopyWithImpl<$Res>
    implements $CouponPubblicoCopyWith<$Res> {
  _$CouponPubblicoCopyWithImpl(this._self, this._then);

  final CouponPubblico _self;
  final $Res Function(CouponPubblico) _then;

/// Create a copy of CouponPubblico
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? codice = null,Object? tipo = null,Object? valore = null,Object? durata = null,Object? periodi = freezed,Object? cumulabile = null,Object? piani = null,Object? validoFino = freezed,}) {
  return _then(CouponPubblico(
codice: null == codice ? _self.codice : codice // ignore: cast_nullable_to_non_nullable
as String,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,valore: null == valore ? _self.valore : valore // ignore: cast_nullable_to_non_nullable
as num,durata: null == durata ? _self.durata : durata // ignore: cast_nullable_to_non_nullable
as String,periodi: freezed == periodi ? _self.periodi : periodi // ignore: cast_nullable_to_non_nullable
as int?,cumulabile: null == cumulabile ? _self.cumulabile : cumulabile // ignore: cast_nullable_to_non_nullable
as bool,piani: null == piani ? _self.piani : piani // ignore: cast_nullable_to_non_nullable
as List<String>,validoFino: freezed == validoFino ? _self.validoFino : validoFino // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [CouponPubblico].
extension CouponPubblicoPatterns on CouponPubblico {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CouponPubblico value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CouponPubblico() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CouponPubblico value)  $default,){
final _that = this;
switch (_that) {
case _CouponPubblico():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CouponPubblico value)?  $default,){
final _that = this;
switch (_that) {
case _CouponPubblico() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String codice,  String tipo,  num valore,  String durata,  int? periodi,  bool cumulabile,  List<String> piani,  String? validoFino)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CouponPubblico() when $default != null:
return $default(_that.codice,_that.tipo,_that.valore,_that.durata,_that.periodi,_that.cumulabile,_that.piani,_that.validoFino);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String codice,  String tipo,  num valore,  String durata,  int? periodi,  bool cumulabile,  List<String> piani,  String? validoFino)  $default,) {final _that = this;
switch (_that) {
case _CouponPubblico():
return $default(_that.codice,_that.tipo,_that.valore,_that.durata,_that.periodi,_that.cumulabile,_that.piani,_that.validoFino);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String codice,  String tipo,  num valore,  String durata,  int? periodi,  bool cumulabile,  List<String> piani,  String? validoFino)?  $default,) {final _that = this;
switch (_that) {
case _CouponPubblico() when $default != null:
return $default(_that.codice,_that.tipo,_that.valore,_that.durata,_that.periodi,_that.cumulabile,_that.piani,_that.validoFino);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CouponPubblico implements CouponPubblico {
  const _CouponPubblico({required this.codice, required this.tipo, required this.valore, required this.durata, this.periodi, this.cumulabile = false,  List<String> piani = const <String>[], this.validoFino}): _piani = piani;
  factory _CouponPubblico.fromJson(Map<String, dynamic> json) => _$CouponPubblicoFromJson(json);

@override final  String codice;
/// `percentuale` o `importo`.
@override final  String tipo;
@override final  num valore;
/// `una_volta`, `periodi`, `sempre`.
@override final  String durata;
@override final  int? periodi;
@override@JsonKey() final  bool cumulabile;
 final  List<String> _piani;
@override@JsonKey() List<String> get piani {
  if (_piani is EqualUnmodifiableListView) return _piani;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_piani);
}

@override final  String? validoFino;

/// Create a copy of CouponPubblico
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CouponPubblicoCopyWith<_CouponPubblico> get copyWith => __$CouponPubblicoCopyWithImpl<_CouponPubblico>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CouponPubblicoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _CouponPubblico&&(identical(other.codice, codice) || other.codice == codice)&&(identical(other.tipo, tipo) || other.tipo == tipo)&&(identical(other.valore, valore) || other.valore == valore)&&(identical(other.durata, durata) || other.durata == durata)&&(identical(other.periodi, periodi) || other.periodi == periodi)&&(identical(other.cumulabile, cumulabile) || other.cumulabile == cumulabile)&&const DeepCollectionEquality().equals(other.piani, _piani)&&(identical(other.validoFino, validoFino) || other.validoFino == validoFino));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,codice,tipo,valore,durata,periodi,cumulabile,const DeepCollectionEquality().hash(_piani),validoFino);
}

@override
String toString() {
    return 'CouponPubblico(codice: $codice, tipo: $tipo, valore: $valore, durata: $durata, periodi: $periodi, cumulabile: $cumulabile, piani: $piani, validoFino: $validoFino)';
}


}

/// @nodoc
abstract mixin class _$CouponPubblicoCopyWith<$Res> implements $CouponPubblicoCopyWith<$Res> {
  factory _$CouponPubblicoCopyWith(_CouponPubblico value, $Res Function(_CouponPubblico) _then) = __$CouponPubblicoCopyWithImpl;
@override @useResult
$Res call({
 String codice, String tipo, num valore, String durata, int? periodi, bool cumulabile, List<String> piani, String? validoFino
});




}
/// @nodoc
class __$CouponPubblicoCopyWithImpl<$Res>
    implements _$CouponPubblicoCopyWith<$Res> {
  __$CouponPubblicoCopyWithImpl(this._self, this._then);

  final _CouponPubblico _self;
  final $Res Function(_CouponPubblico) _then;

/// Create a copy of CouponPubblico
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? codice = null,Object? tipo = null,Object? valore = null,Object? durata = null,Object? periodi = freezed,Object? cumulabile = null,Object? piani = null,Object? validoFino = freezed,}) {
  return _then(_CouponPubblico(
codice: null == codice ? _self.codice : codice // ignore: cast_nullable_to_non_nullable
as String,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,valore: null == valore ? _self.valore : valore // ignore: cast_nullable_to_non_nullable
as num,durata: null == durata ? _self.durata : durata // ignore: cast_nullable_to_non_nullable
as String,periodi: freezed == periodi ? _self.periodi : periodi // ignore: cast_nullable_to_non_nullable
as int?,cumulabile: null == cumulabile ? _self.cumulabile : cumulabile // ignore: cast_nullable_to_non_nullable
as bool,piani: null == piani ? _self._piani : piani // ignore: cast_nullable_to_non_nullable
as List<String>,validoFino: freezed == validoFino ? _self.validoFino : validoFino // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$VoceCoupon {

 String get piano; bool get annuale; bool get rinnovo; bool get prova; String? get motivo; int? get listino; num? get scontoBase; num? get scontoCoupon; num? get sconto; int? get importo; int? get risparmio; String? get vince; bool? get applicato; bool? get cumulabile; num? get scontoRicorrente; int? get rinnoviCoupon; String? get nota;
/// Create a copy of VoceCoupon
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$VoceCouponCopyWith<VoceCoupon> get copyWith => _$VoceCouponCopyWithImpl<VoceCoupon>(this as VoceCoupon, _$identity);

  /// Serializes this VoceCoupon to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as VoceCoupon;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is VoceCoupon&&(identical(other.piano, _this.piano) || other.piano == _this.piano)&&(identical(other.annuale, _this.annuale) || other.annuale == _this.annuale)&&(identical(other.rinnovo, _this.rinnovo) || other.rinnovo == _this.rinnovo)&&(identical(other.prova, _this.prova) || other.prova == _this.prova)&&(identical(other.motivo, _this.motivo) || other.motivo == _this.motivo)&&(identical(other.listino, _this.listino) || other.listino == _this.listino)&&(identical(other.scontoBase, _this.scontoBase) || other.scontoBase == _this.scontoBase)&&(identical(other.scontoCoupon, _this.scontoCoupon) || other.scontoCoupon == _this.scontoCoupon)&&(identical(other.sconto, _this.sconto) || other.sconto == _this.sconto)&&(identical(other.importo, _this.importo) || other.importo == _this.importo)&&(identical(other.risparmio, _this.risparmio) || other.risparmio == _this.risparmio)&&(identical(other.vince, _this.vince) || other.vince == _this.vince)&&(identical(other.applicato, _this.applicato) || other.applicato == _this.applicato)&&(identical(other.cumulabile, _this.cumulabile) || other.cumulabile == _this.cumulabile)&&(identical(other.scontoRicorrente, _this.scontoRicorrente) || other.scontoRicorrente == _this.scontoRicorrente)&&(identical(other.rinnoviCoupon, _this.rinnoviCoupon) || other.rinnoviCoupon == _this.rinnoviCoupon)&&(identical(other.nota, _this.nota) || other.nota == _this.nota));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as VoceCoupon;
  return Object.hash(runtimeType,_this.piano,_this.annuale,_this.rinnovo,_this.prova,_this.motivo,_this.listino,_this.scontoBase,_this.scontoCoupon,_this.sconto,_this.importo,_this.risparmio,_this.vince,_this.applicato,_this.cumulabile,_this.scontoRicorrente,_this.rinnoviCoupon,_this.nota);
}

@override
String toString() {
  final _this = this as VoceCoupon;
  return 'VoceCoupon(piano: ${_this.piano}, annuale: ${_this.annuale}, rinnovo: ${_this.rinnovo}, prova: ${_this.prova}, motivo: ${_this.motivo}, listino: ${_this.listino}, scontoBase: ${_this.scontoBase}, scontoCoupon: ${_this.scontoCoupon}, sconto: ${_this.sconto}, importo: ${_this.importo}, risparmio: ${_this.risparmio}, vince: ${_this.vince}, applicato: ${_this.applicato}, cumulabile: ${_this.cumulabile}, scontoRicorrente: ${_this.scontoRicorrente}, rinnoviCoupon: ${_this.rinnoviCoupon}, nota: ${_this.nota})';
}


}

/// @nodoc
abstract mixin class $VoceCouponCopyWith<$Res>  {
  factory $VoceCouponCopyWith(VoceCoupon value, $Res Function(VoceCoupon) _then) = _$VoceCouponCopyWithImpl;
@useResult
$Res call({
 String piano, bool annuale, bool rinnovo, bool prova, String? motivo, int? listino, num? scontoBase, num? scontoCoupon, num? sconto, int? importo, int? risparmio, String? vince, bool? applicato, bool? cumulabile, num? scontoRicorrente, int? rinnoviCoupon, String? nota
});




}
/// @nodoc
class _$VoceCouponCopyWithImpl<$Res>
    implements $VoceCouponCopyWith<$Res> {
  _$VoceCouponCopyWithImpl(this._self, this._then);

  final VoceCoupon _self;
  final $Res Function(VoceCoupon) _then;

/// Create a copy of VoceCoupon
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? piano = null,Object? annuale = null,Object? rinnovo = null,Object? prova = null,Object? motivo = freezed,Object? listino = freezed,Object? scontoBase = freezed,Object? scontoCoupon = freezed,Object? sconto = freezed,Object? importo = freezed,Object? risparmio = freezed,Object? vince = freezed,Object? applicato = freezed,Object? cumulabile = freezed,Object? scontoRicorrente = freezed,Object? rinnoviCoupon = freezed,Object? nota = freezed,}) {
  return _then(VoceCoupon(
piano: null == piano ? _self.piano : piano // ignore: cast_nullable_to_non_nullable
as String,annuale: null == annuale ? _self.annuale : annuale // ignore: cast_nullable_to_non_nullable
as bool,rinnovo: null == rinnovo ? _self.rinnovo : rinnovo // ignore: cast_nullable_to_non_nullable
as bool,prova: null == prova ? _self.prova : prova // ignore: cast_nullable_to_non_nullable
as bool,motivo: freezed == motivo ? _self.motivo : motivo // ignore: cast_nullable_to_non_nullable
as String?,listino: freezed == listino ? _self.listino : listino // ignore: cast_nullable_to_non_nullable
as int?,scontoBase: freezed == scontoBase ? _self.scontoBase : scontoBase // ignore: cast_nullable_to_non_nullable
as num?,scontoCoupon: freezed == scontoCoupon ? _self.scontoCoupon : scontoCoupon // ignore: cast_nullable_to_non_nullable
as num?,sconto: freezed == sconto ? _self.sconto : sconto // ignore: cast_nullable_to_non_nullable
as num?,importo: freezed == importo ? _self.importo : importo // ignore: cast_nullable_to_non_nullable
as int?,risparmio: freezed == risparmio ? _self.risparmio : risparmio // ignore: cast_nullable_to_non_nullable
as int?,vince: freezed == vince ? _self.vince : vince // ignore: cast_nullable_to_non_nullable
as String?,applicato: freezed == applicato ? _self.applicato : applicato // ignore: cast_nullable_to_non_nullable
as bool?,cumulabile: freezed == cumulabile ? _self.cumulabile : cumulabile // ignore: cast_nullable_to_non_nullable
as bool?,scontoRicorrente: freezed == scontoRicorrente ? _self.scontoRicorrente : scontoRicorrente // ignore: cast_nullable_to_non_nullable
as num?,rinnoviCoupon: freezed == rinnoviCoupon ? _self.rinnoviCoupon : rinnoviCoupon // ignore: cast_nullable_to_non_nullable
as int?,nota: freezed == nota ? _self.nota : nota // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [VoceCoupon].
extension VoceCouponPatterns on VoceCoupon {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _VoceCoupon value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _VoceCoupon() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _VoceCoupon value)  $default,){
final _that = this;
switch (_that) {
case _VoceCoupon():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _VoceCoupon value)?  $default,){
final _that = this;
switch (_that) {
case _VoceCoupon() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String piano,  bool annuale,  bool rinnovo,  bool prova,  String? motivo,  int? listino,  num? scontoBase,  num? scontoCoupon,  num? sconto,  int? importo,  int? risparmio,  String? vince,  bool? applicato,  bool? cumulabile,  num? scontoRicorrente,  int? rinnoviCoupon,  String? nota)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _VoceCoupon() when $default != null:
return $default(_that.piano,_that.annuale,_that.rinnovo,_that.prova,_that.motivo,_that.listino,_that.scontoBase,_that.scontoCoupon,_that.sconto,_that.importo,_that.risparmio,_that.vince,_that.applicato,_that.cumulabile,_that.scontoRicorrente,_that.rinnoviCoupon,_that.nota);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String piano,  bool annuale,  bool rinnovo,  bool prova,  String? motivo,  int? listino,  num? scontoBase,  num? scontoCoupon,  num? sconto,  int? importo,  int? risparmio,  String? vince,  bool? applicato,  bool? cumulabile,  num? scontoRicorrente,  int? rinnoviCoupon,  String? nota)  $default,) {final _that = this;
switch (_that) {
case _VoceCoupon():
return $default(_that.piano,_that.annuale,_that.rinnovo,_that.prova,_that.motivo,_that.listino,_that.scontoBase,_that.scontoCoupon,_that.sconto,_that.importo,_that.risparmio,_that.vince,_that.applicato,_that.cumulabile,_that.scontoRicorrente,_that.rinnoviCoupon,_that.nota);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String piano,  bool annuale,  bool rinnovo,  bool prova,  String? motivo,  int? listino,  num? scontoBase,  num? scontoCoupon,  num? sconto,  int? importo,  int? risparmio,  String? vince,  bool? applicato,  bool? cumulabile,  num? scontoRicorrente,  int? rinnoviCoupon,  String? nota)?  $default,) {final _that = this;
switch (_that) {
case _VoceCoupon() when $default != null:
return $default(_that.piano,_that.annuale,_that.rinnovo,_that.prova,_that.motivo,_that.listino,_that.scontoBase,_that.scontoCoupon,_that.sconto,_that.importo,_that.risparmio,_that.vince,_that.applicato,_that.cumulabile,_that.scontoRicorrente,_that.rinnoviCoupon,_that.nota);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _VoceCoupon implements VoceCoupon {
  const _VoceCoupon({required this.piano, this.annuale = false, this.rinnovo = false, this.prova = false, this.motivo, this.listino, this.scontoBase, this.scontoCoupon, this.sconto, this.importo, this.risparmio, this.vince, this.applicato, this.cumulabile, this.scontoRicorrente, this.rinnoviCoupon, this.nota});
  factory _VoceCoupon.fromJson(Map<String, dynamic> json) => _$VoceCouponFromJson(json);

@override final  String piano;
@override@JsonKey() final  bool annuale;
@override@JsonKey() final  bool rinnovo;
@override@JsonKey() final  bool prova;
@override final  String? motivo;
@override final  int? listino;
@override final  num? scontoBase;
@override final  num? scontoCoupon;
@override final  num? sconto;
@override final  int? importo;
@override final  int? risparmio;
@override final  String? vince;
@override final  bool? applicato;
@override final  bool? cumulabile;
@override final  num? scontoRicorrente;
@override final  int? rinnoviCoupon;
@override final  String? nota;

/// Create a copy of VoceCoupon
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$VoceCouponCopyWith<_VoceCoupon> get copyWith => __$VoceCouponCopyWithImpl<_VoceCoupon>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$VoceCouponToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _VoceCoupon&&(identical(other.piano, piano) || other.piano == piano)&&(identical(other.annuale, annuale) || other.annuale == annuale)&&(identical(other.rinnovo, rinnovo) || other.rinnovo == rinnovo)&&(identical(other.prova, prova) || other.prova == prova)&&(identical(other.motivo, motivo) || other.motivo == motivo)&&(identical(other.listino, listino) || other.listino == listino)&&(identical(other.scontoBase, scontoBase) || other.scontoBase == scontoBase)&&(identical(other.scontoCoupon, scontoCoupon) || other.scontoCoupon == scontoCoupon)&&(identical(other.sconto, sconto) || other.sconto == sconto)&&(identical(other.importo, importo) || other.importo == importo)&&(identical(other.risparmio, risparmio) || other.risparmio == risparmio)&&(identical(other.vince, vince) || other.vince == vince)&&(identical(other.applicato, applicato) || other.applicato == applicato)&&(identical(other.cumulabile, cumulabile) || other.cumulabile == cumulabile)&&(identical(other.scontoRicorrente, scontoRicorrente) || other.scontoRicorrente == scontoRicorrente)&&(identical(other.rinnoviCoupon, rinnoviCoupon) || other.rinnoviCoupon == rinnoviCoupon)&&(identical(other.nota, nota) || other.nota == nota));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,piano,annuale,rinnovo,prova,motivo,listino,scontoBase,scontoCoupon,sconto,importo,risparmio,vince,applicato,cumulabile,scontoRicorrente,rinnoviCoupon,nota);
}

@override
String toString() {
    return 'VoceCoupon(piano: $piano, annuale: $annuale, rinnovo: $rinnovo, prova: $prova, motivo: $motivo, listino: $listino, scontoBase: $scontoBase, scontoCoupon: $scontoCoupon, sconto: $sconto, importo: $importo, risparmio: $risparmio, vince: $vince, applicato: $applicato, cumulabile: $cumulabile, scontoRicorrente: $scontoRicorrente, rinnoviCoupon: $rinnoviCoupon, nota: $nota)';
}


}

/// @nodoc
abstract mixin class _$VoceCouponCopyWith<$Res> implements $VoceCouponCopyWith<$Res> {
  factory _$VoceCouponCopyWith(_VoceCoupon value, $Res Function(_VoceCoupon) _then) = __$VoceCouponCopyWithImpl;
@override @useResult
$Res call({
 String piano, bool annuale, bool rinnovo, bool prova, String? motivo, int? listino, num? scontoBase, num? scontoCoupon, num? sconto, int? importo, int? risparmio, String? vince, bool? applicato, bool? cumulabile, num? scontoRicorrente, int? rinnoviCoupon, String? nota
});




}
/// @nodoc
class __$VoceCouponCopyWithImpl<$Res>
    implements _$VoceCouponCopyWith<$Res> {
  __$VoceCouponCopyWithImpl(this._self, this._then);

  final _VoceCoupon _self;
  final $Res Function(_VoceCoupon) _then;

/// Create a copy of VoceCoupon
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? piano = null,Object? annuale = null,Object? rinnovo = null,Object? prova = null,Object? motivo = freezed,Object? listino = freezed,Object? scontoBase = freezed,Object? scontoCoupon = freezed,Object? sconto = freezed,Object? importo = freezed,Object? risparmio = freezed,Object? vince = freezed,Object? applicato = freezed,Object? cumulabile = freezed,Object? scontoRicorrente = freezed,Object? rinnoviCoupon = freezed,Object? nota = freezed,}) {
  return _then(_VoceCoupon(
piano: null == piano ? _self.piano : piano // ignore: cast_nullable_to_non_nullable
as String,annuale: null == annuale ? _self.annuale : annuale // ignore: cast_nullable_to_non_nullable
as bool,rinnovo: null == rinnovo ? _self.rinnovo : rinnovo // ignore: cast_nullable_to_non_nullable
as bool,prova: null == prova ? _self.prova : prova // ignore: cast_nullable_to_non_nullable
as bool,motivo: freezed == motivo ? _self.motivo : motivo // ignore: cast_nullable_to_non_nullable
as String?,listino: freezed == listino ? _self.listino : listino // ignore: cast_nullable_to_non_nullable
as int?,scontoBase: freezed == scontoBase ? _self.scontoBase : scontoBase // ignore: cast_nullable_to_non_nullable
as num?,scontoCoupon: freezed == scontoCoupon ? _self.scontoCoupon : scontoCoupon // ignore: cast_nullable_to_non_nullable
as num?,sconto: freezed == sconto ? _self.sconto : sconto // ignore: cast_nullable_to_non_nullable
as num?,importo: freezed == importo ? _self.importo : importo // ignore: cast_nullable_to_non_nullable
as int?,risparmio: freezed == risparmio ? _self.risparmio : risparmio // ignore: cast_nullable_to_non_nullable
as int?,vince: freezed == vince ? _self.vince : vince // ignore: cast_nullable_to_non_nullable
as String?,applicato: freezed == applicato ? _self.applicato : applicato // ignore: cast_nullable_to_non_nullable
as bool?,cumulabile: freezed == cumulabile ? _self.cumulabile : cumulabile // ignore: cast_nullable_to_non_nullable
as bool?,scontoRicorrente: freezed == scontoRicorrente ? _self.scontoRicorrente : scontoRicorrente // ignore: cast_nullable_to_non_nullable
as num?,rinnoviCoupon: freezed == rinnoviCoupon ? _self.rinnoviCoupon : rinnoviCoupon // ignore: cast_nullable_to_non_nullable
as int?,nota: freezed == nota ? _self.nota : nota // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$AnteprimaCouponPubblica {

 CouponPubblico get coupon; List<VoceCoupon> get offerte;
/// Create a copy of AnteprimaCouponPubblica
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AnteprimaCouponPubblicaCopyWith<AnteprimaCouponPubblica> get copyWith => _$AnteprimaCouponPubblicaCopyWithImpl<AnteprimaCouponPubblica>(this as AnteprimaCouponPubblica, _$identity);

  /// Serializes this AnteprimaCouponPubblica to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as AnteprimaCouponPubblica;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AnteprimaCouponPubblica&&(identical(other.coupon, _this.coupon) || other.coupon == _this.coupon)&&const DeepCollectionEquality().equals(other.offerte, _this.offerte));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as AnteprimaCouponPubblica;
  return Object.hash(runtimeType,_this.coupon,const DeepCollectionEquality().hash(_this.offerte));
}

@override
String toString() {
  final _this = this as AnteprimaCouponPubblica;
  return 'AnteprimaCouponPubblica(coupon: ${_this.coupon}, offerte: ${_this.offerte})';
}


}

/// @nodoc
abstract mixin class $AnteprimaCouponPubblicaCopyWith<$Res>  {
  factory $AnteprimaCouponPubblicaCopyWith(AnteprimaCouponPubblica value, $Res Function(AnteprimaCouponPubblica) _then) = _$AnteprimaCouponPubblicaCopyWithImpl;
@useResult
$Res call({
 CouponPubblico coupon, List<VoceCoupon> offerte
});


$CouponPubblicoCopyWith<$Res> get coupon;

}
/// @nodoc
class _$AnteprimaCouponPubblicaCopyWithImpl<$Res>
    implements $AnteprimaCouponPubblicaCopyWith<$Res> {
  _$AnteprimaCouponPubblicaCopyWithImpl(this._self, this._then);

  final AnteprimaCouponPubblica _self;
  final $Res Function(AnteprimaCouponPubblica) _then;

/// Create a copy of AnteprimaCouponPubblica
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? coupon = null,Object? offerte = null,}) {
  return _then(AnteprimaCouponPubblica(
coupon: null == coupon ? _self.coupon : coupon // ignore: cast_nullable_to_non_nullable
as CouponPubblico,offerte: null == offerte ? _self.offerte : offerte // ignore: cast_nullable_to_non_nullable
as List<VoceCoupon>,
  ));
}
/// Create a copy of AnteprimaCouponPubblica
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CouponPubblicoCopyWith<$Res> get coupon {
  
  return $CouponPubblicoCopyWith<$Res>(_self.coupon, (value) {
    return _then(_self.copyWith(coupon: value));
  });
}
}


/// Adds pattern-matching-related methods to [AnteprimaCouponPubblica].
extension AnteprimaCouponPubblicaPatterns on AnteprimaCouponPubblica {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _AnteprimaCouponPubblica value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _AnteprimaCouponPubblica() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _AnteprimaCouponPubblica value)  $default,){
final _that = this;
switch (_that) {
case _AnteprimaCouponPubblica():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _AnteprimaCouponPubblica value)?  $default,){
final _that = this;
switch (_that) {
case _AnteprimaCouponPubblica() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( CouponPubblico coupon,  List<VoceCoupon> offerte)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _AnteprimaCouponPubblica() when $default != null:
return $default(_that.coupon,_that.offerte);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( CouponPubblico coupon,  List<VoceCoupon> offerte)  $default,) {final _that = this;
switch (_that) {
case _AnteprimaCouponPubblica():
return $default(_that.coupon,_that.offerte);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( CouponPubblico coupon,  List<VoceCoupon> offerte)?  $default,) {final _that = this;
switch (_that) {
case _AnteprimaCouponPubblica() when $default != null:
return $default(_that.coupon,_that.offerte);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _AnteprimaCouponPubblica extends AnteprimaCouponPubblica {
  const _AnteprimaCouponPubblica({required this.coupon,  List<VoceCoupon> offerte = const <VoceCoupon>[]}): _offerte = offerte,super._();
  factory _AnteprimaCouponPubblica.fromJson(Map<String, dynamic> json) => _$AnteprimaCouponPubblicaFromJson(json);

@override final  CouponPubblico coupon;
 final  List<VoceCoupon> _offerte;
@override@JsonKey() List<VoceCoupon> get offerte {
  if (_offerte is EqualUnmodifiableListView) return _offerte;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_offerte);
}


/// Create a copy of AnteprimaCouponPubblica
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$AnteprimaCouponPubblicaCopyWith<_AnteprimaCouponPubblica> get copyWith => __$AnteprimaCouponPubblicaCopyWithImpl<_AnteprimaCouponPubblica>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$AnteprimaCouponPubblicaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _AnteprimaCouponPubblica&&(identical(other.coupon, coupon) || other.coupon == coupon)&&const DeepCollectionEquality().equals(other.offerte, _offerte));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,coupon,const DeepCollectionEquality().hash(_offerte));
}

@override
String toString() {
    return 'AnteprimaCouponPubblica(coupon: $coupon, offerte: $offerte)';
}


}

/// @nodoc
abstract mixin class _$AnteprimaCouponPubblicaCopyWith<$Res> implements $AnteprimaCouponPubblicaCopyWith<$Res> {
  factory _$AnteprimaCouponPubblicaCopyWith(_AnteprimaCouponPubblica value, $Res Function(_AnteprimaCouponPubblica) _then) = __$AnteprimaCouponPubblicaCopyWithImpl;
@override @useResult
$Res call({
 CouponPubblico coupon, List<VoceCoupon> offerte
});


@override $CouponPubblicoCopyWith<$Res> get coupon;

}
/// @nodoc
class __$AnteprimaCouponPubblicaCopyWithImpl<$Res>
    implements _$AnteprimaCouponPubblicaCopyWith<$Res> {
  __$AnteprimaCouponPubblicaCopyWithImpl(this._self, this._then);

  final _AnteprimaCouponPubblica _self;
  final $Res Function(_AnteprimaCouponPubblica) _then;

/// Create a copy of AnteprimaCouponPubblica
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? coupon = null,Object? offerte = null,}) {
  return _then(_AnteprimaCouponPubblica(
coupon: null == coupon ? _self.coupon : coupon // ignore: cast_nullable_to_non_nullable
as CouponPubblico,offerte: null == offerte ? _self._offerte : offerte // ignore: cast_nullable_to_non_nullable
as List<VoceCoupon>,
  ));
}

/// Create a copy of AnteprimaCouponPubblica
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CouponPubblicoCopyWith<$Res> get coupon {
  
  return $CouponPubblicoCopyWith<$Res>(_self.coupon, (value) {
    return _then(_self.copyWith(coupon: value));
  });
}
}


/// @nodoc
mixin _$Riscatto {

 int get crediti; int get saldo;
/// Create a copy of Riscatto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RiscattoCopyWith<Riscatto> get copyWith => _$RiscattoCopyWithImpl<Riscatto>(this as Riscatto, _$identity);

  /// Serializes this Riscatto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Riscatto;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Riscatto&&(identical(other.crediti, _this.crediti) || other.crediti == _this.crediti)&&(identical(other.saldo, _this.saldo) || other.saldo == _this.saldo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Riscatto;
  return Object.hash(runtimeType,_this.crediti,_this.saldo);
}

@override
String toString() {
  final _this = this as Riscatto;
  return 'Riscatto(crediti: ${_this.crediti}, saldo: ${_this.saldo})';
}


}

/// @nodoc
abstract mixin class $RiscattoCopyWith<$Res>  {
  factory $RiscattoCopyWith(Riscatto value, $Res Function(Riscatto) _then) = _$RiscattoCopyWithImpl;
@useResult
$Res call({
 int crediti, int saldo
});




}
/// @nodoc
class _$RiscattoCopyWithImpl<$Res>
    implements $RiscattoCopyWith<$Res> {
  _$RiscattoCopyWithImpl(this._self, this._then);

  final Riscatto _self;
  final $Res Function(Riscatto) _then;

/// Create a copy of Riscatto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? crediti = null,Object? saldo = null,}) {
  return _then(Riscatto(
crediti: null == crediti ? _self.crediti : crediti // ignore: cast_nullable_to_non_nullable
as int,saldo: null == saldo ? _self.saldo : saldo // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [Riscatto].
extension RiscattoPatterns on Riscatto {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Riscatto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Riscatto() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Riscatto value)  $default,){
final _that = this;
switch (_that) {
case _Riscatto():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Riscatto value)?  $default,){
final _that = this;
switch (_that) {
case _Riscatto() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int crediti,  int saldo)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Riscatto() when $default != null:
return $default(_that.crediti,_that.saldo);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int crediti,  int saldo)  $default,) {final _that = this;
switch (_that) {
case _Riscatto():
return $default(_that.crediti,_that.saldo);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int crediti,  int saldo)?  $default,) {final _that = this;
switch (_that) {
case _Riscatto() when $default != null:
return $default(_that.crediti,_that.saldo);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Riscatto implements Riscatto {
  const _Riscatto({this.crediti = 0, this.saldo = 0});
  factory _Riscatto.fromJson(Map<String, dynamic> json) => _$RiscattoFromJson(json);

@override@JsonKey() final  int crediti;
@override@JsonKey() final  int saldo;

/// Create a copy of Riscatto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RiscattoCopyWith<_Riscatto> get copyWith => __$RiscattoCopyWithImpl<_Riscatto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$RiscattoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Riscatto&&(identical(other.crediti, crediti) || other.crediti == crediti)&&(identical(other.saldo, saldo) || other.saldo == saldo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,crediti,saldo);
}

@override
String toString() {
    return 'Riscatto(crediti: $crediti, saldo: $saldo)';
}


}

/// @nodoc
abstract mixin class _$RiscattoCopyWith<$Res> implements $RiscattoCopyWith<$Res> {
  factory _$RiscattoCopyWith(_Riscatto value, $Res Function(_Riscatto) _then) = __$RiscattoCopyWithImpl;
@override @useResult
$Res call({
 int crediti, int saldo
});




}
/// @nodoc
class __$RiscattoCopyWithImpl<$Res>
    implements _$RiscattoCopyWith<$Res> {
  __$RiscattoCopyWithImpl(this._self, this._then);

  final _Riscatto _self;
  final $Res Function(_Riscatto) _then;

/// Create a copy of Riscatto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? crediti = null,Object? saldo = null,}) {
  return _then(_Riscatto(
crediti: null == crediti ? _self.crediti : crediti // ignore: cast_nullable_to_non_nullable
as int,saldo: null == saldo ? _self.saldo : saldo // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$Mazzo {

 int get id; String get slug; String get nome; String? get descrizione; bool get predefinito; bool get attivo; bool get attivoOra; String? get attivazioneDa; String? get attivazioneFino; int? get prezzoDigitale; int? get prezzoDigitaleScontato; int? get prezzoStampaScontato; int? get prezzoFisicoScontato; List<String> get offertaFormati; bool get offertaAttiva; String? get offertaValidoFino; int? get prezzoStampa; int? get prezzoFisico; bool get richiedeSpedizione; String get valuta; int get rank;
/// Create a copy of Mazzo
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MazzoCopyWith<Mazzo> get copyWith => _$MazzoCopyWithImpl<Mazzo>(this as Mazzo, _$identity);

  /// Serializes this Mazzo to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Mazzo;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Mazzo&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.slug, _this.slug) || other.slug == _this.slug)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.descrizione, _this.descrizione) || other.descrizione == _this.descrizione)&&(identical(other.predefinito, _this.predefinito) || other.predefinito == _this.predefinito)&&(identical(other.attivo, _this.attivo) || other.attivo == _this.attivo)&&(identical(other.attivoOra, _this.attivoOra) || other.attivoOra == _this.attivoOra)&&(identical(other.attivazioneDa, _this.attivazioneDa) || other.attivazioneDa == _this.attivazioneDa)&&(identical(other.attivazioneFino, _this.attivazioneFino) || other.attivazioneFino == _this.attivazioneFino)&&(identical(other.prezzoDigitale, _this.prezzoDigitale) || other.prezzoDigitale == _this.prezzoDigitale)&&(identical(other.prezzoDigitaleScontato, _this.prezzoDigitaleScontato) || other.prezzoDigitaleScontato == _this.prezzoDigitaleScontato)&&(identical(other.prezzoStampaScontato, _this.prezzoStampaScontato) || other.prezzoStampaScontato == _this.prezzoStampaScontato)&&(identical(other.prezzoFisicoScontato, _this.prezzoFisicoScontato) || other.prezzoFisicoScontato == _this.prezzoFisicoScontato)&&const DeepCollectionEquality().equals(other.offertaFormati, _this.offertaFormati)&&(identical(other.offertaAttiva, _this.offertaAttiva) || other.offertaAttiva == _this.offertaAttiva)&&(identical(other.offertaValidoFino, _this.offertaValidoFino) || other.offertaValidoFino == _this.offertaValidoFino)&&(identical(other.prezzoStampa, _this.prezzoStampa) || other.prezzoStampa == _this.prezzoStampa)&&(identical(other.prezzoFisico, _this.prezzoFisico) || other.prezzoFisico == _this.prezzoFisico)&&(identical(other.richiedeSpedizione, _this.richiedeSpedizione) || other.richiedeSpedizione == _this.richiedeSpedizione)&&(identical(other.valuta, _this.valuta) || other.valuta == _this.valuta)&&(identical(other.rank, _this.rank) || other.rank == _this.rank));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Mazzo;
  return Object.hashAll([runtimeType,_this.id,_this.slug,_this.nome,_this.descrizione,_this.predefinito,_this.attivo,_this.attivoOra,_this.attivazioneDa,_this.attivazioneFino,_this.prezzoDigitale,_this.prezzoDigitaleScontato,_this.prezzoStampaScontato,_this.prezzoFisicoScontato,const DeepCollectionEquality().hash(_this.offertaFormati),_this.offertaAttiva,_this.offertaValidoFino,_this.prezzoStampa,_this.prezzoFisico,_this.richiedeSpedizione,_this.valuta,_this.rank]);
}

@override
String toString() {
  final _this = this as Mazzo;
  return 'Mazzo(id: ${_this.id}, slug: ${_this.slug}, nome: ${_this.nome}, descrizione: ${_this.descrizione}, predefinito: ${_this.predefinito}, attivo: ${_this.attivo}, attivoOra: ${_this.attivoOra}, attivazioneDa: ${_this.attivazioneDa}, attivazioneFino: ${_this.attivazioneFino}, prezzoDigitale: ${_this.prezzoDigitale}, prezzoDigitaleScontato: ${_this.prezzoDigitaleScontato}, prezzoStampaScontato: ${_this.prezzoStampaScontato}, prezzoFisicoScontato: ${_this.prezzoFisicoScontato}, offertaFormati: ${_this.offertaFormati}, offertaAttiva: ${_this.offertaAttiva}, offertaValidoFino: ${_this.offertaValidoFino}, prezzoStampa: ${_this.prezzoStampa}, prezzoFisico: ${_this.prezzoFisico}, richiedeSpedizione: ${_this.richiedeSpedizione}, valuta: ${_this.valuta}, rank: ${_this.rank})';
}


}

/// @nodoc
abstract mixin class $MazzoCopyWith<$Res>  {
  factory $MazzoCopyWith(Mazzo value, $Res Function(Mazzo) _then) = _$MazzoCopyWithImpl;
@useResult
$Res call({
 int id, String slug, String nome, String? descrizione, bool predefinito, bool attivo, bool attivoOra, String? attivazioneDa, String? attivazioneFino, int? prezzoDigitale, int? prezzoDigitaleScontato, int? prezzoStampaScontato, int? prezzoFisicoScontato, List<String> offertaFormati, bool offertaAttiva, String? offertaValidoFino, int? prezzoStampa, int? prezzoFisico, bool richiedeSpedizione, String valuta, int rank
});




}
/// @nodoc
class _$MazzoCopyWithImpl<$Res>
    implements $MazzoCopyWith<$Res> {
  _$MazzoCopyWithImpl(this._self, this._then);

  final Mazzo _self;
  final $Res Function(Mazzo) _then;

/// Create a copy of Mazzo
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? slug = null,Object? nome = null,Object? descrizione = freezed,Object? predefinito = null,Object? attivo = null,Object? attivoOra = null,Object? attivazioneDa = freezed,Object? attivazioneFino = freezed,Object? prezzoDigitale = freezed,Object? prezzoDigitaleScontato = freezed,Object? prezzoStampaScontato = freezed,Object? prezzoFisicoScontato = freezed,Object? offertaFormati = null,Object? offertaAttiva = null,Object? offertaValidoFino = freezed,Object? prezzoStampa = freezed,Object? prezzoFisico = freezed,Object? richiedeSpedizione = null,Object? valuta = null,Object? rank = null,}) {
  return _then(Mazzo(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,descrizione: freezed == descrizione ? _self.descrizione : descrizione // ignore: cast_nullable_to_non_nullable
as String?,predefinito: null == predefinito ? _self.predefinito : predefinito // ignore: cast_nullable_to_non_nullable
as bool,attivo: null == attivo ? _self.attivo : attivo // ignore: cast_nullable_to_non_nullable
as bool,attivoOra: null == attivoOra ? _self.attivoOra : attivoOra // ignore: cast_nullable_to_non_nullable
as bool,attivazioneDa: freezed == attivazioneDa ? _self.attivazioneDa : attivazioneDa // ignore: cast_nullable_to_non_nullable
as String?,attivazioneFino: freezed == attivazioneFino ? _self.attivazioneFino : attivazioneFino // ignore: cast_nullable_to_non_nullable
as String?,prezzoDigitale: freezed == prezzoDigitale ? _self.prezzoDigitale : prezzoDigitale // ignore: cast_nullable_to_non_nullable
as int?,prezzoDigitaleScontato: freezed == prezzoDigitaleScontato ? _self.prezzoDigitaleScontato : prezzoDigitaleScontato // ignore: cast_nullable_to_non_nullable
as int?,prezzoStampaScontato: freezed == prezzoStampaScontato ? _self.prezzoStampaScontato : prezzoStampaScontato // ignore: cast_nullable_to_non_nullable
as int?,prezzoFisicoScontato: freezed == prezzoFisicoScontato ? _self.prezzoFisicoScontato : prezzoFisicoScontato // ignore: cast_nullable_to_non_nullable
as int?,offertaFormati: null == offertaFormati ? _self.offertaFormati : offertaFormati // ignore: cast_nullable_to_non_nullable
as List<String>,offertaAttiva: null == offertaAttiva ? _self.offertaAttiva : offertaAttiva // ignore: cast_nullable_to_non_nullable
as bool,offertaValidoFino: freezed == offertaValidoFino ? _self.offertaValidoFino : offertaValidoFino // ignore: cast_nullable_to_non_nullable
as String?,prezzoStampa: freezed == prezzoStampa ? _self.prezzoStampa : prezzoStampa // ignore: cast_nullable_to_non_nullable
as int?,prezzoFisico: freezed == prezzoFisico ? _self.prezzoFisico : prezzoFisico // ignore: cast_nullable_to_non_nullable
as int?,richiedeSpedizione: null == richiedeSpedizione ? _self.richiedeSpedizione : richiedeSpedizione // ignore: cast_nullable_to_non_nullable
as bool,valuta: null == valuta ? _self.valuta : valuta // ignore: cast_nullable_to_non_nullable
as String,rank: null == rank ? _self.rank : rank // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [Mazzo].
extension MazzoPatterns on Mazzo {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Mazzo value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Mazzo() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Mazzo value)  $default,){
final _that = this;
switch (_that) {
case _Mazzo():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Mazzo value)?  $default,){
final _that = this;
switch (_that) {
case _Mazzo() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String slug,  String nome,  String? descrizione,  bool predefinito,  bool attivo,  bool attivoOra,  String? attivazioneDa,  String? attivazioneFino,  int? prezzoDigitale,  int? prezzoDigitaleScontato,  int? prezzoStampaScontato,  int? prezzoFisicoScontato,  List<String> offertaFormati,  bool offertaAttiva,  String? offertaValidoFino,  int? prezzoStampa,  int? prezzoFisico,  bool richiedeSpedizione,  String valuta,  int rank)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Mazzo() when $default != null:
return $default(_that.id,_that.slug,_that.nome,_that.descrizione,_that.predefinito,_that.attivo,_that.attivoOra,_that.attivazioneDa,_that.attivazioneFino,_that.prezzoDigitale,_that.prezzoDigitaleScontato,_that.prezzoStampaScontato,_that.prezzoFisicoScontato,_that.offertaFormati,_that.offertaAttiva,_that.offertaValidoFino,_that.prezzoStampa,_that.prezzoFisico,_that.richiedeSpedizione,_that.valuta,_that.rank);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String slug,  String nome,  String? descrizione,  bool predefinito,  bool attivo,  bool attivoOra,  String? attivazioneDa,  String? attivazioneFino,  int? prezzoDigitale,  int? prezzoDigitaleScontato,  int? prezzoStampaScontato,  int? prezzoFisicoScontato,  List<String> offertaFormati,  bool offertaAttiva,  String? offertaValidoFino,  int? prezzoStampa,  int? prezzoFisico,  bool richiedeSpedizione,  String valuta,  int rank)  $default,) {final _that = this;
switch (_that) {
case _Mazzo():
return $default(_that.id,_that.slug,_that.nome,_that.descrizione,_that.predefinito,_that.attivo,_that.attivoOra,_that.attivazioneDa,_that.attivazioneFino,_that.prezzoDigitale,_that.prezzoDigitaleScontato,_that.prezzoStampaScontato,_that.prezzoFisicoScontato,_that.offertaFormati,_that.offertaAttiva,_that.offertaValidoFino,_that.prezzoStampa,_that.prezzoFisico,_that.richiedeSpedizione,_that.valuta,_that.rank);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String slug,  String nome,  String? descrizione,  bool predefinito,  bool attivo,  bool attivoOra,  String? attivazioneDa,  String? attivazioneFino,  int? prezzoDigitale,  int? prezzoDigitaleScontato,  int? prezzoStampaScontato,  int? prezzoFisicoScontato,  List<String> offertaFormati,  bool offertaAttiva,  String? offertaValidoFino,  int? prezzoStampa,  int? prezzoFisico,  bool richiedeSpedizione,  String valuta,  int rank)?  $default,) {final _that = this;
switch (_that) {
case _Mazzo() when $default != null:
return $default(_that.id,_that.slug,_that.nome,_that.descrizione,_that.predefinito,_that.attivo,_that.attivoOra,_that.attivazioneDa,_that.attivazioneFino,_that.prezzoDigitale,_that.prezzoDigitaleScontato,_that.prezzoStampaScontato,_that.prezzoFisicoScontato,_that.offertaFormati,_that.offertaAttiva,_that.offertaValidoFino,_that.prezzoStampa,_that.prezzoFisico,_that.richiedeSpedizione,_that.valuta,_that.rank);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Mazzo implements Mazzo {
  const _Mazzo({required this.id, required this.slug, required this.nome, this.descrizione, this.predefinito = false, this.attivo = true, this.attivoOra = true, this.attivazioneDa, this.attivazioneFino, this.prezzoDigitale, this.prezzoDigitaleScontato, this.prezzoStampaScontato, this.prezzoFisicoScontato,  List<String> offertaFormati = const <String>[], this.offertaAttiva = false, this.offertaValidoFino, this.prezzoStampa, this.prezzoFisico, this.richiedeSpedizione = false, this.valuta = 'EUR', this.rank = 0}): _offertaFormati = offertaFormati;
  factory _Mazzo.fromJson(Map<String, dynamic> json) => _$MazzoFromJson(json);

@override final  int id;
@override final  String slug;
@override final  String nome;
@override final  String? descrizione;
@override@JsonKey() final  bool predefinito;
@override@JsonKey() final  bool attivo;
@override@JsonKey() final  bool attivoOra;
@override final  String? attivazioneDa;
@override final  String? attivazioneFino;
@override final  int? prezzoDigitale;
@override final  int? prezzoDigitaleScontato;
@override final  int? prezzoStampaScontato;
@override final  int? prezzoFisicoScontato;
 final  List<String> _offertaFormati;
@override@JsonKey() List<String> get offertaFormati {
  if (_offertaFormati is EqualUnmodifiableListView) return _offertaFormati;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_offertaFormati);
}

@override@JsonKey() final  bool offertaAttiva;
@override final  String? offertaValidoFino;
@override final  int? prezzoStampa;
@override final  int? prezzoFisico;
@override@JsonKey() final  bool richiedeSpedizione;
@override@JsonKey() final  String valuta;
@override@JsonKey() final  int rank;

/// Create a copy of Mazzo
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MazzoCopyWith<_Mazzo> get copyWith => __$MazzoCopyWithImpl<_Mazzo>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MazzoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Mazzo&&(identical(other.id, id) || other.id == id)&&(identical(other.slug, slug) || other.slug == slug)&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.descrizione, descrizione) || other.descrizione == descrizione)&&(identical(other.predefinito, predefinito) || other.predefinito == predefinito)&&(identical(other.attivo, attivo) || other.attivo == attivo)&&(identical(other.attivoOra, attivoOra) || other.attivoOra == attivoOra)&&(identical(other.attivazioneDa, attivazioneDa) || other.attivazioneDa == attivazioneDa)&&(identical(other.attivazioneFino, attivazioneFino) || other.attivazioneFino == attivazioneFino)&&(identical(other.prezzoDigitale, prezzoDigitale) || other.prezzoDigitale == prezzoDigitale)&&(identical(other.prezzoDigitaleScontato, prezzoDigitaleScontato) || other.prezzoDigitaleScontato == prezzoDigitaleScontato)&&(identical(other.prezzoStampaScontato, prezzoStampaScontato) || other.prezzoStampaScontato == prezzoStampaScontato)&&(identical(other.prezzoFisicoScontato, prezzoFisicoScontato) || other.prezzoFisicoScontato == prezzoFisicoScontato)&&const DeepCollectionEquality().equals(other.offertaFormati, _offertaFormati)&&(identical(other.offertaAttiva, offertaAttiva) || other.offertaAttiva == offertaAttiva)&&(identical(other.offertaValidoFino, offertaValidoFino) || other.offertaValidoFino == offertaValidoFino)&&(identical(other.prezzoStampa, prezzoStampa) || other.prezzoStampa == prezzoStampa)&&(identical(other.prezzoFisico, prezzoFisico) || other.prezzoFisico == prezzoFisico)&&(identical(other.richiedeSpedizione, richiedeSpedizione) || other.richiedeSpedizione == richiedeSpedizione)&&(identical(other.valuta, valuta) || other.valuta == valuta)&&(identical(other.rank, rank) || other.rank == rank));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hashAll([runtimeType,id,slug,nome,descrizione,predefinito,attivo,attivoOra,attivazioneDa,attivazioneFino,prezzoDigitale,prezzoDigitaleScontato,prezzoStampaScontato,prezzoFisicoScontato,const DeepCollectionEquality().hash(_offertaFormati),offertaAttiva,offertaValidoFino,prezzoStampa,prezzoFisico,richiedeSpedizione,valuta,rank]);
}

@override
String toString() {
    return 'Mazzo(id: $id, slug: $slug, nome: $nome, descrizione: $descrizione, predefinito: $predefinito, attivo: $attivo, attivoOra: $attivoOra, attivazioneDa: $attivazioneDa, attivazioneFino: $attivazioneFino, prezzoDigitale: $prezzoDigitale, prezzoDigitaleScontato: $prezzoDigitaleScontato, prezzoStampaScontato: $prezzoStampaScontato, prezzoFisicoScontato: $prezzoFisicoScontato, offertaFormati: $offertaFormati, offertaAttiva: $offertaAttiva, offertaValidoFino: $offertaValidoFino, prezzoStampa: $prezzoStampa, prezzoFisico: $prezzoFisico, richiedeSpedizione: $richiedeSpedizione, valuta: $valuta, rank: $rank)';
}


}

/// @nodoc
abstract mixin class _$MazzoCopyWith<$Res> implements $MazzoCopyWith<$Res> {
  factory _$MazzoCopyWith(_Mazzo value, $Res Function(_Mazzo) _then) = __$MazzoCopyWithImpl;
@override @useResult
$Res call({
 int id, String slug, String nome, String? descrizione, bool predefinito, bool attivo, bool attivoOra, String? attivazioneDa, String? attivazioneFino, int? prezzoDigitale, int? prezzoDigitaleScontato, int? prezzoStampaScontato, int? prezzoFisicoScontato, List<String> offertaFormati, bool offertaAttiva, String? offertaValidoFino, int? prezzoStampa, int? prezzoFisico, bool richiedeSpedizione, String valuta, int rank
});




}
/// @nodoc
class __$MazzoCopyWithImpl<$Res>
    implements _$MazzoCopyWith<$Res> {
  __$MazzoCopyWithImpl(this._self, this._then);

  final _Mazzo _self;
  final $Res Function(_Mazzo) _then;

/// Create a copy of Mazzo
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slug = null,Object? nome = null,Object? descrizione = freezed,Object? predefinito = null,Object? attivo = null,Object? attivoOra = null,Object? attivazioneDa = freezed,Object? attivazioneFino = freezed,Object? prezzoDigitale = freezed,Object? prezzoDigitaleScontato = freezed,Object? prezzoStampaScontato = freezed,Object? prezzoFisicoScontato = freezed,Object? offertaFormati = null,Object? offertaAttiva = null,Object? offertaValidoFino = freezed,Object? prezzoStampa = freezed,Object? prezzoFisico = freezed,Object? richiedeSpedizione = null,Object? valuta = null,Object? rank = null,}) {
  return _then(_Mazzo(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,descrizione: freezed == descrizione ? _self.descrizione : descrizione // ignore: cast_nullable_to_non_nullable
as String?,predefinito: null == predefinito ? _self.predefinito : predefinito // ignore: cast_nullable_to_non_nullable
as bool,attivo: null == attivo ? _self.attivo : attivo // ignore: cast_nullable_to_non_nullable
as bool,attivoOra: null == attivoOra ? _self.attivoOra : attivoOra // ignore: cast_nullable_to_non_nullable
as bool,attivazioneDa: freezed == attivazioneDa ? _self.attivazioneDa : attivazioneDa // ignore: cast_nullable_to_non_nullable
as String?,attivazioneFino: freezed == attivazioneFino ? _self.attivazioneFino : attivazioneFino // ignore: cast_nullable_to_non_nullable
as String?,prezzoDigitale: freezed == prezzoDigitale ? _self.prezzoDigitale : prezzoDigitale // ignore: cast_nullable_to_non_nullable
as int?,prezzoDigitaleScontato: freezed == prezzoDigitaleScontato ? _self.prezzoDigitaleScontato : prezzoDigitaleScontato // ignore: cast_nullable_to_non_nullable
as int?,prezzoStampaScontato: freezed == prezzoStampaScontato ? _self.prezzoStampaScontato : prezzoStampaScontato // ignore: cast_nullable_to_non_nullable
as int?,prezzoFisicoScontato: freezed == prezzoFisicoScontato ? _self.prezzoFisicoScontato : prezzoFisicoScontato // ignore: cast_nullable_to_non_nullable
as int?,offertaFormati: null == offertaFormati ? _self._offertaFormati : offertaFormati // ignore: cast_nullable_to_non_nullable
as List<String>,offertaAttiva: null == offertaAttiva ? _self.offertaAttiva : offertaAttiva // ignore: cast_nullable_to_non_nullable
as bool,offertaValidoFino: freezed == offertaValidoFino ? _self.offertaValidoFino : offertaValidoFino // ignore: cast_nullable_to_non_nullable
as String?,prezzoStampa: freezed == prezzoStampa ? _self.prezzoStampa : prezzoStampa // ignore: cast_nullable_to_non_nullable
as int?,prezzoFisico: freezed == prezzoFisico ? _self.prezzoFisico : prezzoFisico // ignore: cast_nullable_to_non_nullable
as int?,richiedeSpedizione: null == richiedeSpedizione ? _self.richiedeSpedizione : richiedeSpedizione // ignore: cast_nullable_to_non_nullable
as bool,valuta: null == valuta ? _self.valuta : valuta // ignore: cast_nullable_to_non_nullable
as String,rank: null == rank ? _self.rank : rank // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$MazzoRiga {

 String get nome; String get slug;
/// Create a copy of MazzoRiga
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MazzoRigaCopyWith<MazzoRiga> get copyWith => _$MazzoRigaCopyWithImpl<MazzoRiga>(this as MazzoRiga, _$identity);

  /// Serializes this MazzoRiga to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as MazzoRiga;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is MazzoRiga&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.slug, _this.slug) || other.slug == _this.slug));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as MazzoRiga;
  return Object.hash(runtimeType,_this.nome,_this.slug);
}

@override
String toString() {
  final _this = this as MazzoRiga;
  return 'MazzoRiga(nome: ${_this.nome}, slug: ${_this.slug})';
}


}

/// @nodoc
abstract mixin class $MazzoRigaCopyWith<$Res>  {
  factory $MazzoRigaCopyWith(MazzoRiga value, $Res Function(MazzoRiga) _then) = _$MazzoRigaCopyWithImpl;
@useResult
$Res call({
 String nome, String slug
});




}
/// @nodoc
class _$MazzoRigaCopyWithImpl<$Res>
    implements $MazzoRigaCopyWith<$Res> {
  _$MazzoRigaCopyWithImpl(this._self, this._then);

  final MazzoRiga _self;
  final $Res Function(MazzoRiga) _then;

/// Create a copy of MazzoRiga
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? nome = null,Object? slug = null,}) {
  return _then(MazzoRiga(
nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [MazzoRiga].
extension MazzoRigaPatterns on MazzoRiga {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MazzoRiga value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MazzoRiga() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MazzoRiga value)  $default,){
final _that = this;
switch (_that) {
case _MazzoRiga():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MazzoRiga value)?  $default,){
final _that = this;
switch (_that) {
case _MazzoRiga() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String nome,  String slug)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MazzoRiga() when $default != null:
return $default(_that.nome,_that.slug);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String nome,  String slug)  $default,) {final _that = this;
switch (_that) {
case _MazzoRiga():
return $default(_that.nome,_that.slug);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String nome,  String slug)?  $default,) {final _that = this;
switch (_that) {
case _MazzoRiga() when $default != null:
return $default(_that.nome,_that.slug);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _MazzoRiga implements MazzoRiga {
  const _MazzoRiga({required this.nome, required this.slug});
  factory _MazzoRiga.fromJson(Map<String, dynamic> json) => _$MazzoRigaFromJson(json);

@override final  String nome;
@override final  String slug;

/// Create a copy of MazzoRiga
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MazzoRigaCopyWith<_MazzoRiga> get copyWith => __$MazzoRigaCopyWithImpl<_MazzoRiga>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MazzoRigaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _MazzoRiga&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.slug, slug) || other.slug == slug));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,nome,slug);
}

@override
String toString() {
    return 'MazzoRiga(nome: $nome, slug: $slug)';
}


}

/// @nodoc
abstract mixin class _$MazzoRigaCopyWith<$Res> implements $MazzoRigaCopyWith<$Res> {
  factory _$MazzoRigaCopyWith(_MazzoRiga value, $Res Function(_MazzoRiga) _then) = __$MazzoRigaCopyWithImpl;
@override @useResult
$Res call({
 String nome, String slug
});




}
/// @nodoc
class __$MazzoRigaCopyWithImpl<$Res>
    implements _$MazzoRigaCopyWith<$Res> {
  __$MazzoRigaCopyWithImpl(this._self, this._then);

  final _MazzoRiga _self;
  final $Res Function(_MazzoRiga) _then;

/// Create a copy of MazzoRiga
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? nome = null,Object? slug = null,}) {
  return _then(_MazzoRiga(
nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$RigaOrdine {

 int get id;/// `digitale`, `pdf`, `fisico`.
 String get tipo; int get deckId; MazzoRiga? get mazzo; int get quantita; int get prezzoPienoUnitario; int get prezzoFinaleUnitario; String? get statoEvasione;
/// Create a copy of RigaOrdine
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RigaOrdineCopyWith<RigaOrdine> get copyWith => _$RigaOrdineCopyWithImpl<RigaOrdine>(this as RigaOrdine, _$identity);

  /// Serializes this RigaOrdine to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as RigaOrdine;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RigaOrdine&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.tipo, _this.tipo) || other.tipo == _this.tipo)&&(identical(other.deckId, _this.deckId) || other.deckId == _this.deckId)&&(identical(other.mazzo, _this.mazzo) || other.mazzo == _this.mazzo)&&(identical(other.quantita, _this.quantita) || other.quantita == _this.quantita)&&(identical(other.prezzoPienoUnitario, _this.prezzoPienoUnitario) || other.prezzoPienoUnitario == _this.prezzoPienoUnitario)&&(identical(other.prezzoFinaleUnitario, _this.prezzoFinaleUnitario) || other.prezzoFinaleUnitario == _this.prezzoFinaleUnitario)&&(identical(other.statoEvasione, _this.statoEvasione) || other.statoEvasione == _this.statoEvasione));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as RigaOrdine;
  return Object.hash(runtimeType,_this.id,_this.tipo,_this.deckId,_this.mazzo,_this.quantita,_this.prezzoPienoUnitario,_this.prezzoFinaleUnitario,_this.statoEvasione);
}

@override
String toString() {
  final _this = this as RigaOrdine;
  return 'RigaOrdine(id: ${_this.id}, tipo: ${_this.tipo}, deckId: ${_this.deckId}, mazzo: ${_this.mazzo}, quantita: ${_this.quantita}, prezzoPienoUnitario: ${_this.prezzoPienoUnitario}, prezzoFinaleUnitario: ${_this.prezzoFinaleUnitario}, statoEvasione: ${_this.statoEvasione})';
}


}

/// @nodoc
abstract mixin class $RigaOrdineCopyWith<$Res>  {
  factory $RigaOrdineCopyWith(RigaOrdine value, $Res Function(RigaOrdine) _then) = _$RigaOrdineCopyWithImpl;
@useResult
$Res call({
 int id, String tipo, int deckId, MazzoRiga? mazzo, int quantita, int prezzoPienoUnitario, int prezzoFinaleUnitario, String? statoEvasione
});


$MazzoRigaCopyWith<$Res>? get mazzo;

}
/// @nodoc
class _$RigaOrdineCopyWithImpl<$Res>
    implements $RigaOrdineCopyWith<$Res> {
  _$RigaOrdineCopyWithImpl(this._self, this._then);

  final RigaOrdine _self;
  final $Res Function(RigaOrdine) _then;

/// Create a copy of RigaOrdine
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? tipo = null,Object? deckId = null,Object? mazzo = freezed,Object? quantita = null,Object? prezzoPienoUnitario = null,Object? prezzoFinaleUnitario = null,Object? statoEvasione = freezed,}) {
  return _then(RigaOrdine(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,deckId: null == deckId ? _self.deckId : deckId // ignore: cast_nullable_to_non_nullable
as int,mazzo: freezed == mazzo ? _self.mazzo : mazzo // ignore: cast_nullable_to_non_nullable
as MazzoRiga?,quantita: null == quantita ? _self.quantita : quantita // ignore: cast_nullable_to_non_nullable
as int,prezzoPienoUnitario: null == prezzoPienoUnitario ? _self.prezzoPienoUnitario : prezzoPienoUnitario // ignore: cast_nullable_to_non_nullable
as int,prezzoFinaleUnitario: null == prezzoFinaleUnitario ? _self.prezzoFinaleUnitario : prezzoFinaleUnitario // ignore: cast_nullable_to_non_nullable
as int,statoEvasione: freezed == statoEvasione ? _self.statoEvasione : statoEvasione // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}
/// Create a copy of RigaOrdine
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$MazzoRigaCopyWith<$Res>? get mazzo {
    if (_self.mazzo == null) {
    return null;
  }

  return $MazzoRigaCopyWith<$Res>(_self.mazzo!, (value) {
    return _then(_self.copyWith(mazzo: value));
  });
}
}


/// Adds pattern-matching-related methods to [RigaOrdine].
extension RigaOrdinePatterns on RigaOrdine {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _RigaOrdine value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _RigaOrdine() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _RigaOrdine value)  $default,){
final _that = this;
switch (_that) {
case _RigaOrdine():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _RigaOrdine value)?  $default,){
final _that = this;
switch (_that) {
case _RigaOrdine() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String tipo,  int deckId,  MazzoRiga? mazzo,  int quantita,  int prezzoPienoUnitario,  int prezzoFinaleUnitario,  String? statoEvasione)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _RigaOrdine() when $default != null:
return $default(_that.id,_that.tipo,_that.deckId,_that.mazzo,_that.quantita,_that.prezzoPienoUnitario,_that.prezzoFinaleUnitario,_that.statoEvasione);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String tipo,  int deckId,  MazzoRiga? mazzo,  int quantita,  int prezzoPienoUnitario,  int prezzoFinaleUnitario,  String? statoEvasione)  $default,) {final _that = this;
switch (_that) {
case _RigaOrdine():
return $default(_that.id,_that.tipo,_that.deckId,_that.mazzo,_that.quantita,_that.prezzoPienoUnitario,_that.prezzoFinaleUnitario,_that.statoEvasione);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String tipo,  int deckId,  MazzoRiga? mazzo,  int quantita,  int prezzoPienoUnitario,  int prezzoFinaleUnitario,  String? statoEvasione)?  $default,) {final _that = this;
switch (_that) {
case _RigaOrdine() when $default != null:
return $default(_that.id,_that.tipo,_that.deckId,_that.mazzo,_that.quantita,_that.prezzoPienoUnitario,_that.prezzoFinaleUnitario,_that.statoEvasione);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _RigaOrdine implements RigaOrdine {
  const _RigaOrdine({required this.id, required this.tipo, required this.deckId, this.mazzo, this.quantita = 1, this.prezzoPienoUnitario = 0, this.prezzoFinaleUnitario = 0, this.statoEvasione});
  factory _RigaOrdine.fromJson(Map<String, dynamic> json) => _$RigaOrdineFromJson(json);

@override final  int id;
/// `digitale`, `pdf`, `fisico`.
@override final  String tipo;
@override final  int deckId;
@override final  MazzoRiga? mazzo;
@override@JsonKey() final  int quantita;
@override@JsonKey() final  int prezzoPienoUnitario;
@override@JsonKey() final  int prezzoFinaleUnitario;
@override final  String? statoEvasione;

/// Create a copy of RigaOrdine
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RigaOrdineCopyWith<_RigaOrdine> get copyWith => __$RigaOrdineCopyWithImpl<_RigaOrdine>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$RigaOrdineToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _RigaOrdine&&(identical(other.id, id) || other.id == id)&&(identical(other.tipo, tipo) || other.tipo == tipo)&&(identical(other.deckId, deckId) || other.deckId == deckId)&&(identical(other.mazzo, mazzo) || other.mazzo == mazzo)&&(identical(other.quantita, quantita) || other.quantita == quantita)&&(identical(other.prezzoPienoUnitario, prezzoPienoUnitario) || other.prezzoPienoUnitario == prezzoPienoUnitario)&&(identical(other.prezzoFinaleUnitario, prezzoFinaleUnitario) || other.prezzoFinaleUnitario == prezzoFinaleUnitario)&&(identical(other.statoEvasione, statoEvasione) || other.statoEvasione == statoEvasione));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,tipo,deckId,mazzo,quantita,prezzoPienoUnitario,prezzoFinaleUnitario,statoEvasione);
}

@override
String toString() {
    return 'RigaOrdine(id: $id, tipo: $tipo, deckId: $deckId, mazzo: $mazzo, quantita: $quantita, prezzoPienoUnitario: $prezzoPienoUnitario, prezzoFinaleUnitario: $prezzoFinaleUnitario, statoEvasione: $statoEvasione)';
}


}

/// @nodoc
abstract mixin class _$RigaOrdineCopyWith<$Res> implements $RigaOrdineCopyWith<$Res> {
  factory _$RigaOrdineCopyWith(_RigaOrdine value, $Res Function(_RigaOrdine) _then) = __$RigaOrdineCopyWithImpl;
@override @useResult
$Res call({
 int id, String tipo, int deckId, MazzoRiga? mazzo, int quantita, int prezzoPienoUnitario, int prezzoFinaleUnitario, String? statoEvasione
});


@override $MazzoRigaCopyWith<$Res>? get mazzo;

}
/// @nodoc
class __$RigaOrdineCopyWithImpl<$Res>
    implements _$RigaOrdineCopyWith<$Res> {
  __$RigaOrdineCopyWithImpl(this._self, this._then);

  final _RigaOrdine _self;
  final $Res Function(_RigaOrdine) _then;

/// Create a copy of RigaOrdine
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? tipo = null,Object? deckId = null,Object? mazzo = freezed,Object? quantita = null,Object? prezzoPienoUnitario = null,Object? prezzoFinaleUnitario = null,Object? statoEvasione = freezed,}) {
  return _then(_RigaOrdine(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,deckId: null == deckId ? _self.deckId : deckId // ignore: cast_nullable_to_non_nullable
as int,mazzo: freezed == mazzo ? _self.mazzo : mazzo // ignore: cast_nullable_to_non_nullable
as MazzoRiga?,quantita: null == quantita ? _self.quantita : quantita // ignore: cast_nullable_to_non_nullable
as int,prezzoPienoUnitario: null == prezzoPienoUnitario ? _self.prezzoPienoUnitario : prezzoPienoUnitario // ignore: cast_nullable_to_non_nullable
as int,prezzoFinaleUnitario: null == prezzoFinaleUnitario ? _self.prezzoFinaleUnitario : prezzoFinaleUnitario // ignore: cast_nullable_to_non_nullable
as int,statoEvasione: freezed == statoEvasione ? _self.statoEvasione : statoEvasione // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of RigaOrdine
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$MazzoRigaCopyWith<$Res>? get mazzo {
    if (_self.mazzo == null) {
    return null;
  }

  return $MazzoRigaCopyWith<$Res>(_self.mazzo!, (value) {
    return _then(_self.copyWith(mazzo: value));
  });
}
}


/// @nodoc
mixin _$Ordine {

 String get id; String get status; int get importoTotale; int get scontoScaglioni; String get valuta; List<RigaOrdine> get righe; Map<String, String?>? get indirizzoSpedizione; String? get creato; String? get completato;/// Solo nella risposta di `POST /orders`: dove pagare (`null` se i pagamenti non sono attivi).
 String? get url; bool? get pagamentoAttivo;
/// Create a copy of Ordine
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$OrdineCopyWith<Ordine> get copyWith => _$OrdineCopyWithImpl<Ordine>(this as Ordine, _$identity);

  /// Serializes this Ordine to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Ordine;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Ordine&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.status, _this.status) || other.status == _this.status)&&(identical(other.importoTotale, _this.importoTotale) || other.importoTotale == _this.importoTotale)&&(identical(other.scontoScaglioni, _this.scontoScaglioni) || other.scontoScaglioni == _this.scontoScaglioni)&&(identical(other.valuta, _this.valuta) || other.valuta == _this.valuta)&&const DeepCollectionEquality().equals(other.righe, _this.righe)&&const DeepCollectionEquality().equals(other.indirizzoSpedizione, _this.indirizzoSpedizione)&&(identical(other.creato, _this.creato) || other.creato == _this.creato)&&(identical(other.completato, _this.completato) || other.completato == _this.completato)&&(identical(other.url, _this.url) || other.url == _this.url)&&(identical(other.pagamentoAttivo, _this.pagamentoAttivo) || other.pagamentoAttivo == _this.pagamentoAttivo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Ordine;
  return Object.hash(runtimeType,_this.id,_this.status,_this.importoTotale,_this.scontoScaglioni,_this.valuta,const DeepCollectionEquality().hash(_this.righe),const DeepCollectionEquality().hash(_this.indirizzoSpedizione),_this.creato,_this.completato,_this.url,_this.pagamentoAttivo);
}

@override
String toString() {
  final _this = this as Ordine;
  return 'Ordine(id: ${_this.id}, status: ${_this.status}, importoTotale: ${_this.importoTotale}, scontoScaglioni: ${_this.scontoScaglioni}, valuta: ${_this.valuta}, righe: ${_this.righe}, indirizzoSpedizione: ${_this.indirizzoSpedizione}, creato: ${_this.creato}, completato: ${_this.completato}, url: ${_this.url}, pagamentoAttivo: ${_this.pagamentoAttivo})';
}


}

/// @nodoc
abstract mixin class $OrdineCopyWith<$Res>  {
  factory $OrdineCopyWith(Ordine value, $Res Function(Ordine) _then) = _$OrdineCopyWithImpl;
@useResult
$Res call({
 String id, String status, int importoTotale, int scontoScaglioni, String valuta, List<RigaOrdine> righe, Map<String, String?>? indirizzoSpedizione, String? creato, String? completato, String? url, bool? pagamentoAttivo
});




}
/// @nodoc
class _$OrdineCopyWithImpl<$Res>
    implements $OrdineCopyWith<$Res> {
  _$OrdineCopyWithImpl(this._self, this._then);

  final Ordine _self;
  final $Res Function(Ordine) _then;

/// Create a copy of Ordine
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? status = null,Object? importoTotale = null,Object? scontoScaglioni = null,Object? valuta = null,Object? righe = null,Object? indirizzoSpedizione = freezed,Object? creato = freezed,Object? completato = freezed,Object? url = freezed,Object? pagamentoAttivo = freezed,}) {
  return _then(Ordine(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,importoTotale: null == importoTotale ? _self.importoTotale : importoTotale // ignore: cast_nullable_to_non_nullable
as int,scontoScaglioni: null == scontoScaglioni ? _self.scontoScaglioni : scontoScaglioni // ignore: cast_nullable_to_non_nullable
as int,valuta: null == valuta ? _self.valuta : valuta // ignore: cast_nullable_to_non_nullable
as String,righe: null == righe ? _self.righe : righe // ignore: cast_nullable_to_non_nullable
as List<RigaOrdine>,indirizzoSpedizione: freezed == indirizzoSpedizione ? _self.indirizzoSpedizione : indirizzoSpedizione // ignore: cast_nullable_to_non_nullable
as Map<String, String?>?,creato: freezed == creato ? _self.creato : creato // ignore: cast_nullable_to_non_nullable
as String?,completato: freezed == completato ? _self.completato : completato // ignore: cast_nullable_to_non_nullable
as String?,url: freezed == url ? _self.url : url // ignore: cast_nullable_to_non_nullable
as String?,pagamentoAttivo: freezed == pagamentoAttivo ? _self.pagamentoAttivo : pagamentoAttivo // ignore: cast_nullable_to_non_nullable
as bool?,
  ));
}

}


/// Adds pattern-matching-related methods to [Ordine].
extension OrdinePatterns on Ordine {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Ordine value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Ordine() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Ordine value)  $default,){
final _that = this;
switch (_that) {
case _Ordine():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Ordine value)?  $default,){
final _that = this;
switch (_that) {
case _Ordine() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String status,  int importoTotale,  int scontoScaglioni,  String valuta,  List<RigaOrdine> righe,  Map<String, String?>? indirizzoSpedizione,  String? creato,  String? completato,  String? url,  bool? pagamentoAttivo)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Ordine() when $default != null:
return $default(_that.id,_that.status,_that.importoTotale,_that.scontoScaglioni,_that.valuta,_that.righe,_that.indirizzoSpedizione,_that.creato,_that.completato,_that.url,_that.pagamentoAttivo);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String status,  int importoTotale,  int scontoScaglioni,  String valuta,  List<RigaOrdine> righe,  Map<String, String?>? indirizzoSpedizione,  String? creato,  String? completato,  String? url,  bool? pagamentoAttivo)  $default,) {final _that = this;
switch (_that) {
case _Ordine():
return $default(_that.id,_that.status,_that.importoTotale,_that.scontoScaglioni,_that.valuta,_that.righe,_that.indirizzoSpedizione,_that.creato,_that.completato,_that.url,_that.pagamentoAttivo);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String status,  int importoTotale,  int scontoScaglioni,  String valuta,  List<RigaOrdine> righe,  Map<String, String?>? indirizzoSpedizione,  String? creato,  String? completato,  String? url,  bool? pagamentoAttivo)?  $default,) {final _that = this;
switch (_that) {
case _Ordine() when $default != null:
return $default(_that.id,_that.status,_that.importoTotale,_that.scontoScaglioni,_that.valuta,_that.righe,_that.indirizzoSpedizione,_that.creato,_that.completato,_that.url,_that.pagamentoAttivo);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Ordine implements Ordine {
  const _Ordine({required this.id, required this.status, this.importoTotale = 0, this.scontoScaglioni = 0, this.valuta = 'EUR',  List<RigaOrdine> righe = const <RigaOrdine>[],  Map<String, String?>? indirizzoSpedizione, this.creato, this.completato, this.url, this.pagamentoAttivo}): _righe = righe,_indirizzoSpedizione = indirizzoSpedizione;
  factory _Ordine.fromJson(Map<String, dynamic> json) => _$OrdineFromJson(json);

@override final  String id;
@override final  String status;
@override@JsonKey() final  int importoTotale;
@override@JsonKey() final  int scontoScaglioni;
@override@JsonKey() final  String valuta;
 final  List<RigaOrdine> _righe;
@override@JsonKey() List<RigaOrdine> get righe {
  if (_righe is EqualUnmodifiableListView) return _righe;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_righe);
}

 final  Map<String, String?>? _indirizzoSpedizione;
@override Map<String, String?>? get indirizzoSpedizione {
  final value = _indirizzoSpedizione;
  if (value == null) return null;
  if (_indirizzoSpedizione is EqualUnmodifiableMapView) return _indirizzoSpedizione;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override final  String? creato;
@override final  String? completato;
/// Solo nella risposta di `POST /orders`: dove pagare (`null` se i pagamenti non sono attivi).
@override final  String? url;
@override final  bool? pagamentoAttivo;

/// Create a copy of Ordine
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$OrdineCopyWith<_Ordine> get copyWith => __$OrdineCopyWithImpl<_Ordine>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$OrdineToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Ordine&&(identical(other.id, id) || other.id == id)&&(identical(other.status, status) || other.status == status)&&(identical(other.importoTotale, importoTotale) || other.importoTotale == importoTotale)&&(identical(other.scontoScaglioni, scontoScaglioni) || other.scontoScaglioni == scontoScaglioni)&&(identical(other.valuta, valuta) || other.valuta == valuta)&&const DeepCollectionEquality().equals(other.righe, _righe)&&const DeepCollectionEquality().equals(other.indirizzoSpedizione, _indirizzoSpedizione)&&(identical(other.creato, creato) || other.creato == creato)&&(identical(other.completato, completato) || other.completato == completato)&&(identical(other.url, url) || other.url == url)&&(identical(other.pagamentoAttivo, pagamentoAttivo) || other.pagamentoAttivo == pagamentoAttivo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,status,importoTotale,scontoScaglioni,valuta,const DeepCollectionEquality().hash(_righe),const DeepCollectionEquality().hash(_indirizzoSpedizione),creato,completato,url,pagamentoAttivo);
}

@override
String toString() {
    return 'Ordine(id: $id, status: $status, importoTotale: $importoTotale, scontoScaglioni: $scontoScaglioni, valuta: $valuta, righe: $righe, indirizzoSpedizione: $indirizzoSpedizione, creato: $creato, completato: $completato, url: $url, pagamentoAttivo: $pagamentoAttivo)';
}


}

/// @nodoc
abstract mixin class _$OrdineCopyWith<$Res> implements $OrdineCopyWith<$Res> {
  factory _$OrdineCopyWith(_Ordine value, $Res Function(_Ordine) _then) = __$OrdineCopyWithImpl;
@override @useResult
$Res call({
 String id, String status, int importoTotale, int scontoScaglioni, String valuta, List<RigaOrdine> righe, Map<String, String?>? indirizzoSpedizione, String? creato, String? completato, String? url, bool? pagamentoAttivo
});




}
/// @nodoc
class __$OrdineCopyWithImpl<$Res>
    implements _$OrdineCopyWith<$Res> {
  __$OrdineCopyWithImpl(this._self, this._then);

  final _Ordine _self;
  final $Res Function(_Ordine) _then;

/// Create a copy of Ordine
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? status = null,Object? importoTotale = null,Object? scontoScaglioni = null,Object? valuta = null,Object? righe = null,Object? indirizzoSpedizione = freezed,Object? creato = freezed,Object? completato = freezed,Object? url = freezed,Object? pagamentoAttivo = freezed,}) {
  return _then(_Ordine(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,importoTotale: null == importoTotale ? _self.importoTotale : importoTotale // ignore: cast_nullable_to_non_nullable
as int,scontoScaglioni: null == scontoScaglioni ? _self.scontoScaglioni : scontoScaglioni // ignore: cast_nullable_to_non_nullable
as int,valuta: null == valuta ? _self.valuta : valuta // ignore: cast_nullable_to_non_nullable
as String,righe: null == righe ? _self._righe : righe // ignore: cast_nullable_to_non_nullable
as List<RigaOrdine>,indirizzoSpedizione: freezed == indirizzoSpedizione ? _self._indirizzoSpedizione : indirizzoSpedizione // ignore: cast_nullable_to_non_nullable
as Map<String, String?>?,creato: freezed == creato ? _self.creato : creato // ignore: cast_nullable_to_non_nullable
as String?,completato: freezed == completato ? _self.completato : completato // ignore: cast_nullable_to_non_nullable
as String?,url: freezed == url ? _self.url : url // ignore: cast_nullable_to_non_nullable
as String?,pagamentoAttivo: freezed == pagamentoAttivo ? _self.pagamentoAttivo : pagamentoAttivo // ignore: cast_nullable_to_non_nullable
as bool?,
  ));
}


}


/// @nodoc
mixin _$RigaPreventivo {

 int get deckId; String get tipo; int get quantita; int get prezzoPienoUnitario; int get prezzoFinaleUnitario;
/// Create a copy of RigaPreventivo
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RigaPreventivoCopyWith<RigaPreventivo> get copyWith => _$RigaPreventivoCopyWithImpl<RigaPreventivo>(this as RigaPreventivo, _$identity);

  /// Serializes this RigaPreventivo to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as RigaPreventivo;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RigaPreventivo&&(identical(other.deckId, _this.deckId) || other.deckId == _this.deckId)&&(identical(other.tipo, _this.tipo) || other.tipo == _this.tipo)&&(identical(other.quantita, _this.quantita) || other.quantita == _this.quantita)&&(identical(other.prezzoPienoUnitario, _this.prezzoPienoUnitario) || other.prezzoPienoUnitario == _this.prezzoPienoUnitario)&&(identical(other.prezzoFinaleUnitario, _this.prezzoFinaleUnitario) || other.prezzoFinaleUnitario == _this.prezzoFinaleUnitario));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as RigaPreventivo;
  return Object.hash(runtimeType,_this.deckId,_this.tipo,_this.quantita,_this.prezzoPienoUnitario,_this.prezzoFinaleUnitario);
}

@override
String toString() {
  final _this = this as RigaPreventivo;
  return 'RigaPreventivo(deckId: ${_this.deckId}, tipo: ${_this.tipo}, quantita: ${_this.quantita}, prezzoPienoUnitario: ${_this.prezzoPienoUnitario}, prezzoFinaleUnitario: ${_this.prezzoFinaleUnitario})';
}


}

/// @nodoc
abstract mixin class $RigaPreventivoCopyWith<$Res>  {
  factory $RigaPreventivoCopyWith(RigaPreventivo value, $Res Function(RigaPreventivo) _then) = _$RigaPreventivoCopyWithImpl;
@useResult
$Res call({
 int deckId, String tipo, int quantita, int prezzoPienoUnitario, int prezzoFinaleUnitario
});




}
/// @nodoc
class _$RigaPreventivoCopyWithImpl<$Res>
    implements $RigaPreventivoCopyWith<$Res> {
  _$RigaPreventivoCopyWithImpl(this._self, this._then);

  final RigaPreventivo _self;
  final $Res Function(RigaPreventivo) _then;

/// Create a copy of RigaPreventivo
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? deckId = null,Object? tipo = null,Object? quantita = null,Object? prezzoPienoUnitario = null,Object? prezzoFinaleUnitario = null,}) {
  return _then(RigaPreventivo(
deckId: null == deckId ? _self.deckId : deckId // ignore: cast_nullable_to_non_nullable
as int,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,quantita: null == quantita ? _self.quantita : quantita // ignore: cast_nullable_to_non_nullable
as int,prezzoPienoUnitario: null == prezzoPienoUnitario ? _self.prezzoPienoUnitario : prezzoPienoUnitario // ignore: cast_nullable_to_non_nullable
as int,prezzoFinaleUnitario: null == prezzoFinaleUnitario ? _self.prezzoFinaleUnitario : prezzoFinaleUnitario // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [RigaPreventivo].
extension RigaPreventivoPatterns on RigaPreventivo {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _RigaPreventivo value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _RigaPreventivo() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _RigaPreventivo value)  $default,){
final _that = this;
switch (_that) {
case _RigaPreventivo():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _RigaPreventivo value)?  $default,){
final _that = this;
switch (_that) {
case _RigaPreventivo() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int deckId,  String tipo,  int quantita,  int prezzoPienoUnitario,  int prezzoFinaleUnitario)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _RigaPreventivo() when $default != null:
return $default(_that.deckId,_that.tipo,_that.quantita,_that.prezzoPienoUnitario,_that.prezzoFinaleUnitario);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int deckId,  String tipo,  int quantita,  int prezzoPienoUnitario,  int prezzoFinaleUnitario)  $default,) {final _that = this;
switch (_that) {
case _RigaPreventivo():
return $default(_that.deckId,_that.tipo,_that.quantita,_that.prezzoPienoUnitario,_that.prezzoFinaleUnitario);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int deckId,  String tipo,  int quantita,  int prezzoPienoUnitario,  int prezzoFinaleUnitario)?  $default,) {final _that = this;
switch (_that) {
case _RigaPreventivo() when $default != null:
return $default(_that.deckId,_that.tipo,_that.quantita,_that.prezzoPienoUnitario,_that.prezzoFinaleUnitario);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _RigaPreventivo implements RigaPreventivo {
  const _RigaPreventivo({required this.deckId, required this.tipo, this.quantita = 1, this.prezzoPienoUnitario = 0, this.prezzoFinaleUnitario = 0});
  factory _RigaPreventivo.fromJson(Map<String, dynamic> json) => _$RigaPreventivoFromJson(json);

@override final  int deckId;
@override final  String tipo;
@override@JsonKey() final  int quantita;
@override@JsonKey() final  int prezzoPienoUnitario;
@override@JsonKey() final  int prezzoFinaleUnitario;

/// Create a copy of RigaPreventivo
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RigaPreventivoCopyWith<_RigaPreventivo> get copyWith => __$RigaPreventivoCopyWithImpl<_RigaPreventivo>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$RigaPreventivoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _RigaPreventivo&&(identical(other.deckId, deckId) || other.deckId == deckId)&&(identical(other.tipo, tipo) || other.tipo == tipo)&&(identical(other.quantita, quantita) || other.quantita == quantita)&&(identical(other.prezzoPienoUnitario, prezzoPienoUnitario) || other.prezzoPienoUnitario == prezzoPienoUnitario)&&(identical(other.prezzoFinaleUnitario, prezzoFinaleUnitario) || other.prezzoFinaleUnitario == prezzoFinaleUnitario));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,deckId,tipo,quantita,prezzoPienoUnitario,prezzoFinaleUnitario);
}

@override
String toString() {
    return 'RigaPreventivo(deckId: $deckId, tipo: $tipo, quantita: $quantita, prezzoPienoUnitario: $prezzoPienoUnitario, prezzoFinaleUnitario: $prezzoFinaleUnitario)';
}


}

/// @nodoc
abstract mixin class _$RigaPreventivoCopyWith<$Res> implements $RigaPreventivoCopyWith<$Res> {
  factory _$RigaPreventivoCopyWith(_RigaPreventivo value, $Res Function(_RigaPreventivo) _then) = __$RigaPreventivoCopyWithImpl;
@override @useResult
$Res call({
 int deckId, String tipo, int quantita, int prezzoPienoUnitario, int prezzoFinaleUnitario
});




}
/// @nodoc
class __$RigaPreventivoCopyWithImpl<$Res>
    implements _$RigaPreventivoCopyWith<$Res> {
  __$RigaPreventivoCopyWithImpl(this._self, this._then);

  final _RigaPreventivo _self;
  final $Res Function(_RigaPreventivo) _then;

/// Create a copy of RigaPreventivo
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? deckId = null,Object? tipo = null,Object? quantita = null,Object? prezzoPienoUnitario = null,Object? prezzoFinaleUnitario = null,}) {
  return _then(_RigaPreventivo(
deckId: null == deckId ? _self.deckId : deckId // ignore: cast_nullable_to_non_nullable
as int,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,quantita: null == quantita ? _self.quantita : quantita // ignore: cast_nullable_to_non_nullable
as int,prezzoPienoUnitario: null == prezzoPienoUnitario ? _self.prezzoPienoUnitario : prezzoPienoUnitario // ignore: cast_nullable_to_non_nullable
as int,prezzoFinaleUnitario: null == prezzoFinaleUnitario ? _self.prezzoFinaleUnitario : prezzoFinaleUnitario // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$Preventivo {

 List<RigaPreventivo> get righe; int get subtotale; num get scaglionePercentuale; int get scontoScaglioni; int get totale; bool get richiedeIndirizzo; bool get pagamentoAttivo;
/// Create a copy of Preventivo
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PreventivoCopyWith<Preventivo> get copyWith => _$PreventivoCopyWithImpl<Preventivo>(this as Preventivo, _$identity);

  /// Serializes this Preventivo to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Preventivo;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Preventivo&&const DeepCollectionEquality().equals(other.righe, _this.righe)&&(identical(other.subtotale, _this.subtotale) || other.subtotale == _this.subtotale)&&(identical(other.scaglionePercentuale, _this.scaglionePercentuale) || other.scaglionePercentuale == _this.scaglionePercentuale)&&(identical(other.scontoScaglioni, _this.scontoScaglioni) || other.scontoScaglioni == _this.scontoScaglioni)&&(identical(other.totale, _this.totale) || other.totale == _this.totale)&&(identical(other.richiedeIndirizzo, _this.richiedeIndirizzo) || other.richiedeIndirizzo == _this.richiedeIndirizzo)&&(identical(other.pagamentoAttivo, _this.pagamentoAttivo) || other.pagamentoAttivo == _this.pagamentoAttivo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Preventivo;
  return Object.hash(runtimeType,const DeepCollectionEquality().hash(_this.righe),_this.subtotale,_this.scaglionePercentuale,_this.scontoScaglioni,_this.totale,_this.richiedeIndirizzo,_this.pagamentoAttivo);
}

@override
String toString() {
  final _this = this as Preventivo;
  return 'Preventivo(righe: ${_this.righe}, subtotale: ${_this.subtotale}, scaglionePercentuale: ${_this.scaglionePercentuale}, scontoScaglioni: ${_this.scontoScaglioni}, totale: ${_this.totale}, richiedeIndirizzo: ${_this.richiedeIndirizzo}, pagamentoAttivo: ${_this.pagamentoAttivo})';
}


}

/// @nodoc
abstract mixin class $PreventivoCopyWith<$Res>  {
  factory $PreventivoCopyWith(Preventivo value, $Res Function(Preventivo) _then) = _$PreventivoCopyWithImpl;
@useResult
$Res call({
 List<RigaPreventivo> righe, int subtotale, num scaglionePercentuale, int scontoScaglioni, int totale, bool richiedeIndirizzo, bool pagamentoAttivo
});




}
/// @nodoc
class _$PreventivoCopyWithImpl<$Res>
    implements $PreventivoCopyWith<$Res> {
  _$PreventivoCopyWithImpl(this._self, this._then);

  final Preventivo _self;
  final $Res Function(Preventivo) _then;

/// Create a copy of Preventivo
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? righe = null,Object? subtotale = null,Object? scaglionePercentuale = null,Object? scontoScaglioni = null,Object? totale = null,Object? richiedeIndirizzo = null,Object? pagamentoAttivo = null,}) {
  return _then(Preventivo(
righe: null == righe ? _self.righe : righe // ignore: cast_nullable_to_non_nullable
as List<RigaPreventivo>,subtotale: null == subtotale ? _self.subtotale : subtotale // ignore: cast_nullable_to_non_nullable
as int,scaglionePercentuale: null == scaglionePercentuale ? _self.scaglionePercentuale : scaglionePercentuale // ignore: cast_nullable_to_non_nullable
as num,scontoScaglioni: null == scontoScaglioni ? _self.scontoScaglioni : scontoScaglioni // ignore: cast_nullable_to_non_nullable
as int,totale: null == totale ? _self.totale : totale // ignore: cast_nullable_to_non_nullable
as int,richiedeIndirizzo: null == richiedeIndirizzo ? _self.richiedeIndirizzo : richiedeIndirizzo // ignore: cast_nullable_to_non_nullable
as bool,pagamentoAttivo: null == pagamentoAttivo ? _self.pagamentoAttivo : pagamentoAttivo // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [Preventivo].
extension PreventivoPatterns on Preventivo {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Preventivo value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Preventivo() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Preventivo value)  $default,){
final _that = this;
switch (_that) {
case _Preventivo():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Preventivo value)?  $default,){
final _that = this;
switch (_that) {
case _Preventivo() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( List<RigaPreventivo> righe,  int subtotale,  num scaglionePercentuale,  int scontoScaglioni,  int totale,  bool richiedeIndirizzo,  bool pagamentoAttivo)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Preventivo() when $default != null:
return $default(_that.righe,_that.subtotale,_that.scaglionePercentuale,_that.scontoScaglioni,_that.totale,_that.richiedeIndirizzo,_that.pagamentoAttivo);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( List<RigaPreventivo> righe,  int subtotale,  num scaglionePercentuale,  int scontoScaglioni,  int totale,  bool richiedeIndirizzo,  bool pagamentoAttivo)  $default,) {final _that = this;
switch (_that) {
case _Preventivo():
return $default(_that.righe,_that.subtotale,_that.scaglionePercentuale,_that.scontoScaglioni,_that.totale,_that.richiedeIndirizzo,_that.pagamentoAttivo);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( List<RigaPreventivo> righe,  int subtotale,  num scaglionePercentuale,  int scontoScaglioni,  int totale,  bool richiedeIndirizzo,  bool pagamentoAttivo)?  $default,) {final _that = this;
switch (_that) {
case _Preventivo() when $default != null:
return $default(_that.righe,_that.subtotale,_that.scaglionePercentuale,_that.scontoScaglioni,_that.totale,_that.richiedeIndirizzo,_that.pagamentoAttivo);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Preventivo implements Preventivo {
  const _Preventivo({ List<RigaPreventivo> righe = const <RigaPreventivo>[], this.subtotale = 0, this.scaglionePercentuale = 0, this.scontoScaglioni = 0, this.totale = 0, this.richiedeIndirizzo = false, this.pagamentoAttivo = false}): _righe = righe;
  factory _Preventivo.fromJson(Map<String, dynamic> json) => _$PreventivoFromJson(json);

 final  List<RigaPreventivo> _righe;
@override@JsonKey() List<RigaPreventivo> get righe {
  if (_righe is EqualUnmodifiableListView) return _righe;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_righe);
}

@override@JsonKey() final  int subtotale;
@override@JsonKey() final  num scaglionePercentuale;
@override@JsonKey() final  int scontoScaglioni;
@override@JsonKey() final  int totale;
@override@JsonKey() final  bool richiedeIndirizzo;
@override@JsonKey() final  bool pagamentoAttivo;

/// Create a copy of Preventivo
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PreventivoCopyWith<_Preventivo> get copyWith => __$PreventivoCopyWithImpl<_Preventivo>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PreventivoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Preventivo&&const DeepCollectionEquality().equals(other.righe, _righe)&&(identical(other.subtotale, subtotale) || other.subtotale == subtotale)&&(identical(other.scaglionePercentuale, scaglionePercentuale) || other.scaglionePercentuale == scaglionePercentuale)&&(identical(other.scontoScaglioni, scontoScaglioni) || other.scontoScaglioni == scontoScaglioni)&&(identical(other.totale, totale) || other.totale == totale)&&(identical(other.richiedeIndirizzo, richiedeIndirizzo) || other.richiedeIndirizzo == richiedeIndirizzo)&&(identical(other.pagamentoAttivo, pagamentoAttivo) || other.pagamentoAttivo == pagamentoAttivo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,const DeepCollectionEquality().hash(_righe),subtotale,scaglionePercentuale,scontoScaglioni,totale,richiedeIndirizzo,pagamentoAttivo);
}

@override
String toString() {
    return 'Preventivo(righe: $righe, subtotale: $subtotale, scaglionePercentuale: $scaglionePercentuale, scontoScaglioni: $scontoScaglioni, totale: $totale, richiedeIndirizzo: $richiedeIndirizzo, pagamentoAttivo: $pagamentoAttivo)';
}


}

/// @nodoc
abstract mixin class _$PreventivoCopyWith<$Res> implements $PreventivoCopyWith<$Res> {
  factory _$PreventivoCopyWith(_Preventivo value, $Res Function(_Preventivo) _then) = __$PreventivoCopyWithImpl;
@override @useResult
$Res call({
 List<RigaPreventivo> righe, int subtotale, num scaglionePercentuale, int scontoScaglioni, int totale, bool richiedeIndirizzo, bool pagamentoAttivo
});




}
/// @nodoc
class __$PreventivoCopyWithImpl<$Res>
    implements _$PreventivoCopyWith<$Res> {
  __$PreventivoCopyWithImpl(this._self, this._then);

  final _Preventivo _self;
  final $Res Function(_Preventivo) _then;

/// Create a copy of Preventivo
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? righe = null,Object? subtotale = null,Object? scaglionePercentuale = null,Object? scontoScaglioni = null,Object? totale = null,Object? richiedeIndirizzo = null,Object? pagamentoAttivo = null,}) {
  return _then(_Preventivo(
righe: null == righe ? _self._righe : righe // ignore: cast_nullable_to_non_nullable
as List<RigaPreventivo>,subtotale: null == subtotale ? _self.subtotale : subtotale // ignore: cast_nullable_to_non_nullable
as int,scaglionePercentuale: null == scaglionePercentuale ? _self.scaglionePercentuale : scaglionePercentuale // ignore: cast_nullable_to_non_nullable
as num,scontoScaglioni: null == scontoScaglioni ? _self.scontoScaglioni : scontoScaglioni // ignore: cast_nullable_to_non_nullable
as int,totale: null == totale ? _self.totale : totale // ignore: cast_nullable_to_non_nullable
as int,richiedeIndirizzo: null == richiedeIndirizzo ? _self.richiedeIndirizzo : richiedeIndirizzo // ignore: cast_nullable_to_non_nullable
as bool,pagamentoAttivo: null == pagamentoAttivo ? _self.pagamentoAttivo : pagamentoAttivo // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}


/// @nodoc
mixin _$Indirizzo {

 String get id; String get nome; String get via; String get citta; String get cap; String? get provincia; String get paese; String? get telefono; bool get predefinito;
/// Create a copy of Indirizzo
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$IndirizzoCopyWith<Indirizzo> get copyWith => _$IndirizzoCopyWithImpl<Indirizzo>(this as Indirizzo, _$identity);

  /// Serializes this Indirizzo to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Indirizzo;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Indirizzo&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.via, _this.via) || other.via == _this.via)&&(identical(other.citta, _this.citta) || other.citta == _this.citta)&&(identical(other.cap, _this.cap) || other.cap == _this.cap)&&(identical(other.provincia, _this.provincia) || other.provincia == _this.provincia)&&(identical(other.paese, _this.paese) || other.paese == _this.paese)&&(identical(other.telefono, _this.telefono) || other.telefono == _this.telefono)&&(identical(other.predefinito, _this.predefinito) || other.predefinito == _this.predefinito));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Indirizzo;
  return Object.hash(runtimeType,_this.id,_this.nome,_this.via,_this.citta,_this.cap,_this.provincia,_this.paese,_this.telefono,_this.predefinito);
}

@override
String toString() {
  final _this = this as Indirizzo;
  return 'Indirizzo(id: ${_this.id}, nome: ${_this.nome}, via: ${_this.via}, citta: ${_this.citta}, cap: ${_this.cap}, provincia: ${_this.provincia}, paese: ${_this.paese}, telefono: ${_this.telefono}, predefinito: ${_this.predefinito})';
}


}

/// @nodoc
abstract mixin class $IndirizzoCopyWith<$Res>  {
  factory $IndirizzoCopyWith(Indirizzo value, $Res Function(Indirizzo) _then) = _$IndirizzoCopyWithImpl;
@useResult
$Res call({
 String id, String nome, String via, String citta, String cap, String? provincia, String paese, String? telefono, bool predefinito
});




}
/// @nodoc
class _$IndirizzoCopyWithImpl<$Res>
    implements $IndirizzoCopyWith<$Res> {
  _$IndirizzoCopyWithImpl(this._self, this._then);

  final Indirizzo _self;
  final $Res Function(Indirizzo) _then;

/// Create a copy of Indirizzo
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? nome = null,Object? via = null,Object? citta = null,Object? cap = null,Object? provincia = freezed,Object? paese = null,Object? telefono = freezed,Object? predefinito = null,}) {
  return _then(Indirizzo(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,via: null == via ? _self.via : via // ignore: cast_nullable_to_non_nullable
as String,citta: null == citta ? _self.citta : citta // ignore: cast_nullable_to_non_nullable
as String,cap: null == cap ? _self.cap : cap // ignore: cast_nullable_to_non_nullable
as String,provincia: freezed == provincia ? _self.provincia : provincia // ignore: cast_nullable_to_non_nullable
as String?,paese: null == paese ? _self.paese : paese // ignore: cast_nullable_to_non_nullable
as String,telefono: freezed == telefono ? _self.telefono : telefono // ignore: cast_nullable_to_non_nullable
as String?,predefinito: null == predefinito ? _self.predefinito : predefinito // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [Indirizzo].
extension IndirizzoPatterns on Indirizzo {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Indirizzo value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Indirizzo() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Indirizzo value)  $default,){
final _that = this;
switch (_that) {
case _Indirizzo():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Indirizzo value)?  $default,){
final _that = this;
switch (_that) {
case _Indirizzo() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String nome,  String via,  String citta,  String cap,  String? provincia,  String paese,  String? telefono,  bool predefinito)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Indirizzo() when $default != null:
return $default(_that.id,_that.nome,_that.via,_that.citta,_that.cap,_that.provincia,_that.paese,_that.telefono,_that.predefinito);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String nome,  String via,  String citta,  String cap,  String? provincia,  String paese,  String? telefono,  bool predefinito)  $default,) {final _that = this;
switch (_that) {
case _Indirizzo():
return $default(_that.id,_that.nome,_that.via,_that.citta,_that.cap,_that.provincia,_that.paese,_that.telefono,_that.predefinito);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String nome,  String via,  String citta,  String cap,  String? provincia,  String paese,  String? telefono,  bool predefinito)?  $default,) {final _that = this;
switch (_that) {
case _Indirizzo() when $default != null:
return $default(_that.id,_that.nome,_that.via,_that.citta,_that.cap,_that.provincia,_that.paese,_that.telefono,_that.predefinito);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Indirizzo implements Indirizzo {
  const _Indirizzo({required this.id, required this.nome, required this.via, required this.citta, required this.cap, this.provincia, required this.paese, this.telefono, this.predefinito = false});
  factory _Indirizzo.fromJson(Map<String, dynamic> json) => _$IndirizzoFromJson(json);

@override final  String id;
@override final  String nome;
@override final  String via;
@override final  String citta;
@override final  String cap;
@override final  String? provincia;
@override final  String paese;
@override final  String? telefono;
@override@JsonKey() final  bool predefinito;

/// Create a copy of Indirizzo
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$IndirizzoCopyWith<_Indirizzo> get copyWith => __$IndirizzoCopyWithImpl<_Indirizzo>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$IndirizzoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Indirizzo&&(identical(other.id, id) || other.id == id)&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.via, via) || other.via == via)&&(identical(other.citta, citta) || other.citta == citta)&&(identical(other.cap, cap) || other.cap == cap)&&(identical(other.provincia, provincia) || other.provincia == provincia)&&(identical(other.paese, paese) || other.paese == paese)&&(identical(other.telefono, telefono) || other.telefono == telefono)&&(identical(other.predefinito, predefinito) || other.predefinito == predefinito));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,nome,via,citta,cap,provincia,paese,telefono,predefinito);
}

@override
String toString() {
    return 'Indirizzo(id: $id, nome: $nome, via: $via, citta: $citta, cap: $cap, provincia: $provincia, paese: $paese, telefono: $telefono, predefinito: $predefinito)';
}


}

/// @nodoc
abstract mixin class _$IndirizzoCopyWith<$Res> implements $IndirizzoCopyWith<$Res> {
  factory _$IndirizzoCopyWith(_Indirizzo value, $Res Function(_Indirizzo) _then) = __$IndirizzoCopyWithImpl;
@override @useResult
$Res call({
 String id, String nome, String via, String citta, String cap, String? provincia, String paese, String? telefono, bool predefinito
});




}
/// @nodoc
class __$IndirizzoCopyWithImpl<$Res>
    implements _$IndirizzoCopyWith<$Res> {
  __$IndirizzoCopyWithImpl(this._self, this._then);

  final _Indirizzo _self;
  final $Res Function(_Indirizzo) _then;

/// Create a copy of Indirizzo
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? nome = null,Object? via = null,Object? citta = null,Object? cap = null,Object? provincia = freezed,Object? paese = null,Object? telefono = freezed,Object? predefinito = null,}) {
  return _then(_Indirizzo(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,via: null == via ? _self.via : via // ignore: cast_nullable_to_non_nullable
as String,citta: null == citta ? _self.citta : citta // ignore: cast_nullable_to_non_nullable
as String,cap: null == cap ? _self.cap : cap // ignore: cast_nullable_to_non_nullable
as String,provincia: freezed == provincia ? _self.provincia : provincia // ignore: cast_nullable_to_non_nullable
as String?,paese: null == paese ? _self.paese : paese // ignore: cast_nullable_to_non_nullable
as String,telefono: freezed == telefono ? _self.telefono : telefono // ignore: cast_nullable_to_non_nullable
as String?,predefinito: null == predefinito ? _self.predefinito : predefinito // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}

// dart format on

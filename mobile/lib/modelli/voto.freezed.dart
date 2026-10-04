// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'voto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$CampioneVoto {

 String? get etichetta; String? get url; String? get mini;
/// Create a copy of CampioneVoto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CampioneVotoCopyWith<CampioneVoto> get copyWith => _$CampioneVotoCopyWithImpl<CampioneVoto>(this as CampioneVoto, _$identity);

  /// Serializes this CampioneVoto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as CampioneVoto;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CampioneVoto&&(identical(other.etichetta, _this.etichetta) || other.etichetta == _this.etichetta)&&(identical(other.url, _this.url) || other.url == _this.url)&&(identical(other.mini, _this.mini) || other.mini == _this.mini));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as CampioneVoto;
  return Object.hash(runtimeType,_this.etichetta,_this.url,_this.mini);
}

@override
String toString() {
  final _this = this as CampioneVoto;
  return 'CampioneVoto(etichetta: ${_this.etichetta}, url: ${_this.url}, mini: ${_this.mini})';
}


}

/// @nodoc
abstract mixin class $CampioneVotoCopyWith<$Res>  {
  factory $CampioneVotoCopyWith(CampioneVoto value, $Res Function(CampioneVoto) _then) = _$CampioneVotoCopyWithImpl;
@useResult
$Res call({
 String? etichetta, String? url, String? mini
});




}
/// @nodoc
class _$CampioneVotoCopyWithImpl<$Res>
    implements $CampioneVotoCopyWith<$Res> {
  _$CampioneVotoCopyWithImpl(this._self, this._then);

  final CampioneVoto _self;
  final $Res Function(CampioneVoto) _then;

/// Create a copy of CampioneVoto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? etichetta = freezed,Object? url = freezed,Object? mini = freezed,}) {
  return _then(CampioneVoto(
etichetta: freezed == etichetta ? _self.etichetta : etichetta // ignore: cast_nullable_to_non_nullable
as String?,url: freezed == url ? _self.url : url // ignore: cast_nullable_to_non_nullable
as String?,mini: freezed == mini ? _self.mini : mini // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [CampioneVoto].
extension CampioneVotoPatterns on CampioneVoto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CampioneVoto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CampioneVoto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CampioneVoto value)  $default,){
final _that = this;
switch (_that) {
case _CampioneVoto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CampioneVoto value)?  $default,){
final _that = this;
switch (_that) {
case _CampioneVoto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? etichetta,  String? url,  String? mini)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CampioneVoto() when $default != null:
return $default(_that.etichetta,_that.url,_that.mini);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? etichetta,  String? url,  String? mini)  $default,) {final _that = this;
switch (_that) {
case _CampioneVoto():
return $default(_that.etichetta,_that.url,_that.mini);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? etichetta,  String? url,  String? mini)?  $default,) {final _that = this;
switch (_that) {
case _CampioneVoto() when $default != null:
return $default(_that.etichetta,_that.url,_that.mini);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CampioneVoto implements CampioneVoto {
  const _CampioneVoto({this.etichetta, this.url, this.mini});
  factory _CampioneVoto.fromJson(Map<String, dynamic> json) => _$CampioneVotoFromJson(json);

@override final  String? etichetta;
@override final  String? url;
@override final  String? mini;

/// Create a copy of CampioneVoto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CampioneVotoCopyWith<_CampioneVoto> get copyWith => __$CampioneVotoCopyWithImpl<_CampioneVoto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CampioneVotoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _CampioneVoto&&(identical(other.etichetta, etichetta) || other.etichetta == etichetta)&&(identical(other.url, url) || other.url == url)&&(identical(other.mini, mini) || other.mini == mini));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,etichetta,url,mini);
}

@override
String toString() {
    return 'CampioneVoto(etichetta: $etichetta, url: $url, mini: $mini)';
}


}

/// @nodoc
abstract mixin class _$CampioneVotoCopyWith<$Res> implements $CampioneVotoCopyWith<$Res> {
  factory _$CampioneVotoCopyWith(_CampioneVoto value, $Res Function(_CampioneVoto) _then) = __$CampioneVotoCopyWithImpl;
@override @useResult
$Res call({
 String? etichetta, String? url, String? mini
});




}
/// @nodoc
class __$CampioneVotoCopyWithImpl<$Res>
    implements _$CampioneVotoCopyWith<$Res> {
  __$CampioneVotoCopyWithImpl(this._self, this._then);

  final _CampioneVoto _self;
  final $Res Function(_CampioneVoto) _then;

/// Create a copy of CampioneVoto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? etichetta = freezed,Object? url = freezed,Object? mini = freezed,}) {
  return _then(_CampioneVoto(
etichetta: freezed == etichetta ? _self.etichetta : etichetta // ignore: cast_nullable_to_non_nullable
as String?,url: freezed == url ? _self.url : url // ignore: cast_nullable_to_non_nullable
as String?,mini: freezed == mini ? _self.mini : mini // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$CandidatoVoto {

 String get id; String get nome; String? get descrizione; List<CampioneVoto> get campioni;/// `null` finché non si è votato in questa tornata: le percentuali non si mostrano prima.
 num? get percentuale;
/// Create a copy of CandidatoVoto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CandidatoVotoCopyWith<CandidatoVoto> get copyWith => _$CandidatoVotoCopyWithImpl<CandidatoVoto>(this as CandidatoVoto, _$identity);

  /// Serializes this CandidatoVoto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as CandidatoVoto;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CandidatoVoto&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.descrizione, _this.descrizione) || other.descrizione == _this.descrizione)&&const DeepCollectionEquality().equals(other.campioni, _this.campioni)&&(identical(other.percentuale, _this.percentuale) || other.percentuale == _this.percentuale));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as CandidatoVoto;
  return Object.hash(runtimeType,_this.id,_this.nome,_this.descrizione,const DeepCollectionEquality().hash(_this.campioni),_this.percentuale);
}

@override
String toString() {
  final _this = this as CandidatoVoto;
  return 'CandidatoVoto(id: ${_this.id}, nome: ${_this.nome}, descrizione: ${_this.descrizione}, campioni: ${_this.campioni}, percentuale: ${_this.percentuale})';
}


}

/// @nodoc
abstract mixin class $CandidatoVotoCopyWith<$Res>  {
  factory $CandidatoVotoCopyWith(CandidatoVoto value, $Res Function(CandidatoVoto) _then) = _$CandidatoVotoCopyWithImpl;
@useResult
$Res call({
 String id, String nome, String? descrizione, List<CampioneVoto> campioni, num? percentuale
});




}
/// @nodoc
class _$CandidatoVotoCopyWithImpl<$Res>
    implements $CandidatoVotoCopyWith<$Res> {
  _$CandidatoVotoCopyWithImpl(this._self, this._then);

  final CandidatoVoto _self;
  final $Res Function(CandidatoVoto) _then;

/// Create a copy of CandidatoVoto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? nome = null,Object? descrizione = freezed,Object? campioni = null,Object? percentuale = freezed,}) {
  return _then(CandidatoVoto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,descrizione: freezed == descrizione ? _self.descrizione : descrizione // ignore: cast_nullable_to_non_nullable
as String?,campioni: null == campioni ? _self.campioni : campioni // ignore: cast_nullable_to_non_nullable
as List<CampioneVoto>,percentuale: freezed == percentuale ? _self.percentuale : percentuale // ignore: cast_nullable_to_non_nullable
as num?,
  ));
}

}


/// Adds pattern-matching-related methods to [CandidatoVoto].
extension CandidatoVotoPatterns on CandidatoVoto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CandidatoVoto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CandidatoVoto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CandidatoVoto value)  $default,){
final _that = this;
switch (_that) {
case _CandidatoVoto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CandidatoVoto value)?  $default,){
final _that = this;
switch (_that) {
case _CandidatoVoto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String nome,  String? descrizione,  List<CampioneVoto> campioni,  num? percentuale)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CandidatoVoto() when $default != null:
return $default(_that.id,_that.nome,_that.descrizione,_that.campioni,_that.percentuale);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String nome,  String? descrizione,  List<CampioneVoto> campioni,  num? percentuale)  $default,) {final _that = this;
switch (_that) {
case _CandidatoVoto():
return $default(_that.id,_that.nome,_that.descrizione,_that.campioni,_that.percentuale);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String nome,  String? descrizione,  List<CampioneVoto> campioni,  num? percentuale)?  $default,) {final _that = this;
switch (_that) {
case _CandidatoVoto() when $default != null:
return $default(_that.id,_that.nome,_that.descrizione,_that.campioni,_that.percentuale);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CandidatoVoto implements CandidatoVoto {
  const _CandidatoVoto({required this.id, required this.nome, this.descrizione,  List<CampioneVoto> campioni = const <CampioneVoto>[], this.percentuale}): _campioni = campioni;
  factory _CandidatoVoto.fromJson(Map<String, dynamic> json) => _$CandidatoVotoFromJson(json);

@override final  String id;
@override final  String nome;
@override final  String? descrizione;
 final  List<CampioneVoto> _campioni;
@override@JsonKey() List<CampioneVoto> get campioni {
  if (_campioni is EqualUnmodifiableListView) return _campioni;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_campioni);
}

/// `null` finché non si è votato in questa tornata: le percentuali non si mostrano prima.
@override final  num? percentuale;

/// Create a copy of CandidatoVoto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CandidatoVotoCopyWith<_CandidatoVoto> get copyWith => __$CandidatoVotoCopyWithImpl<_CandidatoVoto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CandidatoVotoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _CandidatoVoto&&(identical(other.id, id) || other.id == id)&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.descrizione, descrizione) || other.descrizione == descrizione)&&const DeepCollectionEquality().equals(other.campioni, _campioni)&&(identical(other.percentuale, percentuale) || other.percentuale == percentuale));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,nome,descrizione,const DeepCollectionEquality().hash(_campioni),percentuale);
}

@override
String toString() {
    return 'CandidatoVoto(id: $id, nome: $nome, descrizione: $descrizione, campioni: $campioni, percentuale: $percentuale)';
}


}

/// @nodoc
abstract mixin class _$CandidatoVotoCopyWith<$Res> implements $CandidatoVotoCopyWith<$Res> {
  factory _$CandidatoVotoCopyWith(_CandidatoVoto value, $Res Function(_CandidatoVoto) _then) = __$CandidatoVotoCopyWithImpl;
@override @useResult
$Res call({
 String id, String nome, String? descrizione, List<CampioneVoto> campioni, num? percentuale
});




}
/// @nodoc
class __$CandidatoVotoCopyWithImpl<$Res>
    implements _$CandidatoVotoCopyWith<$Res> {
  __$CandidatoVotoCopyWithImpl(this._self, this._then);

  final _CandidatoVoto _self;
  final $Res Function(_CandidatoVoto) _then;

/// Create a copy of CandidatoVoto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? nome = null,Object? descrizione = freezed,Object? campioni = null,Object? percentuale = freezed,}) {
  return _then(_CandidatoVoto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,descrizione: freezed == descrizione ? _self.descrizione : descrizione // ignore: cast_nullable_to_non_nullable
as String?,campioni: null == campioni ? _self._campioni : campioni // ignore: cast_nullable_to_non_nullable
as List<CampioneVoto>,percentuale: freezed == percentuale ? _self.percentuale : percentuale // ignore: cast_nullable_to_non_nullable
as num?,
  ));
}


}


/// @nodoc
mixin _$VincitorePrecedente {

 String get nome; num get percentuale;
/// Create a copy of VincitorePrecedente
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$VincitorePrecedenteCopyWith<VincitorePrecedente> get copyWith => _$VincitorePrecedenteCopyWithImpl<VincitorePrecedente>(this as VincitorePrecedente, _$identity);

  /// Serializes this VincitorePrecedente to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as VincitorePrecedente;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is VincitorePrecedente&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.percentuale, _this.percentuale) || other.percentuale == _this.percentuale));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as VincitorePrecedente;
  return Object.hash(runtimeType,_this.nome,_this.percentuale);
}

@override
String toString() {
  final _this = this as VincitorePrecedente;
  return 'VincitorePrecedente(nome: ${_this.nome}, percentuale: ${_this.percentuale})';
}


}

/// @nodoc
abstract mixin class $VincitorePrecedenteCopyWith<$Res>  {
  factory $VincitorePrecedenteCopyWith(VincitorePrecedente value, $Res Function(VincitorePrecedente) _then) = _$VincitorePrecedenteCopyWithImpl;
@useResult
$Res call({
 String nome, num percentuale
});




}
/// @nodoc
class _$VincitorePrecedenteCopyWithImpl<$Res>
    implements $VincitorePrecedenteCopyWith<$Res> {
  _$VincitorePrecedenteCopyWithImpl(this._self, this._then);

  final VincitorePrecedente _self;
  final $Res Function(VincitorePrecedente) _then;

/// Create a copy of VincitorePrecedente
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? nome = null,Object? percentuale = null,}) {
  return _then(VincitorePrecedente(
nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,percentuale: null == percentuale ? _self.percentuale : percentuale // ignore: cast_nullable_to_non_nullable
as num,
  ));
}

}


/// Adds pattern-matching-related methods to [VincitorePrecedente].
extension VincitorePrecedentePatterns on VincitorePrecedente {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _VincitorePrecedente value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _VincitorePrecedente() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _VincitorePrecedente value)  $default,){
final _that = this;
switch (_that) {
case _VincitorePrecedente():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _VincitorePrecedente value)?  $default,){
final _that = this;
switch (_that) {
case _VincitorePrecedente() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String nome,  num percentuale)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _VincitorePrecedente() when $default != null:
return $default(_that.nome,_that.percentuale);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String nome,  num percentuale)  $default,) {final _that = this;
switch (_that) {
case _VincitorePrecedente():
return $default(_that.nome,_that.percentuale);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String nome,  num percentuale)?  $default,) {final _that = this;
switch (_that) {
case _VincitorePrecedente() when $default != null:
return $default(_that.nome,_that.percentuale);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _VincitorePrecedente implements VincitorePrecedente {
  const _VincitorePrecedente({required this.nome, required this.percentuale});
  factory _VincitorePrecedente.fromJson(Map<String, dynamic> json) => _$VincitorePrecedenteFromJson(json);

@override final  String nome;
@override final  num percentuale;

/// Create a copy of VincitorePrecedente
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$VincitorePrecedenteCopyWith<_VincitorePrecedente> get copyWith => __$VincitorePrecedenteCopyWithImpl<_VincitorePrecedente>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$VincitorePrecedenteToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _VincitorePrecedente&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.percentuale, percentuale) || other.percentuale == percentuale));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,nome,percentuale);
}

@override
String toString() {
    return 'VincitorePrecedente(nome: $nome, percentuale: $percentuale)';
}


}

/// @nodoc
abstract mixin class _$VincitorePrecedenteCopyWith<$Res> implements $VincitorePrecedenteCopyWith<$Res> {
  factory _$VincitorePrecedenteCopyWith(_VincitorePrecedente value, $Res Function(_VincitorePrecedente) _then) = __$VincitorePrecedenteCopyWithImpl;
@override @useResult
$Res call({
 String nome, num percentuale
});




}
/// @nodoc
class __$VincitorePrecedenteCopyWithImpl<$Res>
    implements _$VincitorePrecedenteCopyWith<$Res> {
  __$VincitorePrecedenteCopyWithImpl(this._self, this._then);

  final _VincitorePrecedente _self;
  final $Res Function(_VincitorePrecedente) _then;

/// Create a copy of VincitorePrecedente
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? nome = null,Object? percentuale = null,}) {
  return _then(_VincitorePrecedente(
nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,percentuale: null == percentuale ? _self.percentuale : percentuale // ignore: cast_nullable_to_non_nullable
as num,
  ));
}


}


/// @nodoc
mixin _$Tornata {

 String get id;
/// Create a copy of Tornata
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$TornataCopyWith<Tornata> get copyWith => _$TornataCopyWithImpl<Tornata>(this as Tornata, _$identity);

  /// Serializes this Tornata to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Tornata;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Tornata&&(identical(other.id, _this.id) || other.id == _this.id));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Tornata;
  return Object.hash(runtimeType,_this.id);
}

@override
String toString() {
  final _this = this as Tornata;
  return 'Tornata(id: ${_this.id})';
}


}

/// @nodoc
abstract mixin class $TornataCopyWith<$Res>  {
  factory $TornataCopyWith(Tornata value, $Res Function(Tornata) _then) = _$TornataCopyWithImpl;
@useResult
$Res call({
 String id
});




}
/// @nodoc
class _$TornataCopyWithImpl<$Res>
    implements $TornataCopyWith<$Res> {
  _$TornataCopyWithImpl(this._self, this._then);

  final Tornata _self;
  final $Res Function(Tornata) _then;

/// Create a copy of Tornata
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,}) {
  return _then(Tornata(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [Tornata].
extension TornataPatterns on Tornata {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Tornata value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Tornata() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Tornata value)  $default,){
final _that = this;
switch (_that) {
case _Tornata():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Tornata value)?  $default,){
final _that = this;
switch (_that) {
case _Tornata() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Tornata() when $default != null:
return $default(_that.id);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id)  $default,) {final _that = this;
switch (_that) {
case _Tornata():
return $default(_that.id);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id)?  $default,) {final _that = this;
switch (_that) {
case _Tornata() when $default != null:
return $default(_that.id);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Tornata implements Tornata {
  const _Tornata({required this.id});
  factory _Tornata.fromJson(Map<String, dynamic> json) => _$TornataFromJson(json);

@override final  String id;

/// Create a copy of Tornata
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$TornataCopyWith<_Tornata> get copyWith => __$TornataCopyWithImpl<_Tornata>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$TornataToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Tornata&&(identical(other.id, id) || other.id == id));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id);
}

@override
String toString() {
    return 'Tornata(id: $id)';
}


}

/// @nodoc
abstract mixin class _$TornataCopyWith<$Res> implements $TornataCopyWith<$Res> {
  factory _$TornataCopyWith(_Tornata value, $Res Function(_Tornata) _then) = __$TornataCopyWithImpl;
@override @useResult
$Res call({
 String id
});




}
/// @nodoc
class __$TornataCopyWithImpl<$Res>
    implements _$TornataCopyWith<$Res> {
  __$TornataCopyWithImpl(this._self, this._then);

  final _Tornata _self;
  final $Res Function(_Tornata) _then;

/// Create a copy of Tornata
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,}) {
  return _then(_Tornata(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$StatoVoto {

 Tornata? get tornata; String? get mioVoto; List<CandidatoVoto> get candidati; List<VincitorePrecedente>? get vincitoriPrecedenti;
/// Create a copy of StatoVoto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$StatoVotoCopyWith<StatoVoto> get copyWith => _$StatoVotoCopyWithImpl<StatoVoto>(this as StatoVoto, _$identity);

  /// Serializes this StatoVoto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as StatoVoto;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is StatoVoto&&(identical(other.tornata, _this.tornata) || other.tornata == _this.tornata)&&(identical(other.mioVoto, _this.mioVoto) || other.mioVoto == _this.mioVoto)&&const DeepCollectionEquality().equals(other.candidati, _this.candidati)&&const DeepCollectionEquality().equals(other.vincitoriPrecedenti, _this.vincitoriPrecedenti));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as StatoVoto;
  return Object.hash(runtimeType,_this.tornata,_this.mioVoto,const DeepCollectionEquality().hash(_this.candidati),const DeepCollectionEquality().hash(_this.vincitoriPrecedenti));
}

@override
String toString() {
  final _this = this as StatoVoto;
  return 'StatoVoto(tornata: ${_this.tornata}, mioVoto: ${_this.mioVoto}, candidati: ${_this.candidati}, vincitoriPrecedenti: ${_this.vincitoriPrecedenti})';
}


}

/// @nodoc
abstract mixin class $StatoVotoCopyWith<$Res>  {
  factory $StatoVotoCopyWith(StatoVoto value, $Res Function(StatoVoto) _then) = _$StatoVotoCopyWithImpl;
@useResult
$Res call({
 Tornata? tornata, String? mioVoto, List<CandidatoVoto> candidati, List<VincitorePrecedente>? vincitoriPrecedenti
});


$TornataCopyWith<$Res>? get tornata;

}
/// @nodoc
class _$StatoVotoCopyWithImpl<$Res>
    implements $StatoVotoCopyWith<$Res> {
  _$StatoVotoCopyWithImpl(this._self, this._then);

  final StatoVoto _self;
  final $Res Function(StatoVoto) _then;

/// Create a copy of StatoVoto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? tornata = freezed,Object? mioVoto = freezed,Object? candidati = null,Object? vincitoriPrecedenti = freezed,}) {
  return _then(StatoVoto(
tornata: freezed == tornata ? _self.tornata : tornata // ignore: cast_nullable_to_non_nullable
as Tornata?,mioVoto: freezed == mioVoto ? _self.mioVoto : mioVoto // ignore: cast_nullable_to_non_nullable
as String?,candidati: null == candidati ? _self.candidati : candidati // ignore: cast_nullable_to_non_nullable
as List<CandidatoVoto>,vincitoriPrecedenti: freezed == vincitoriPrecedenti ? _self.vincitoriPrecedenti : vincitoriPrecedenti // ignore: cast_nullable_to_non_nullable
as List<VincitorePrecedente>?,
  ));
}
/// Create a copy of StatoVoto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$TornataCopyWith<$Res>? get tornata {
    if (_self.tornata == null) {
    return null;
  }

  return $TornataCopyWith<$Res>(_self.tornata!, (value) {
    return _then(_self.copyWith(tornata: value));
  });
}
}


/// Adds pattern-matching-related methods to [StatoVoto].
extension StatoVotoPatterns on StatoVoto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _StatoVoto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _StatoVoto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _StatoVoto value)  $default,){
final _that = this;
switch (_that) {
case _StatoVoto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _StatoVoto value)?  $default,){
final _that = this;
switch (_that) {
case _StatoVoto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( Tornata? tornata,  String? mioVoto,  List<CandidatoVoto> candidati,  List<VincitorePrecedente>? vincitoriPrecedenti)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _StatoVoto() when $default != null:
return $default(_that.tornata,_that.mioVoto,_that.candidati,_that.vincitoriPrecedenti);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( Tornata? tornata,  String? mioVoto,  List<CandidatoVoto> candidati,  List<VincitorePrecedente>? vincitoriPrecedenti)  $default,) {final _that = this;
switch (_that) {
case _StatoVoto():
return $default(_that.tornata,_that.mioVoto,_that.candidati,_that.vincitoriPrecedenti);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( Tornata? tornata,  String? mioVoto,  List<CandidatoVoto> candidati,  List<VincitorePrecedente>? vincitoriPrecedenti)?  $default,) {final _that = this;
switch (_that) {
case _StatoVoto() when $default != null:
return $default(_that.tornata,_that.mioVoto,_that.candidati,_that.vincitoriPrecedenti);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _StatoVoto implements StatoVoto {
  const _StatoVoto({this.tornata, this.mioVoto,  List<CandidatoVoto> candidati = const <CandidatoVoto>[],  List<VincitorePrecedente>? vincitoriPrecedenti}): _candidati = candidati,_vincitoriPrecedenti = vincitoriPrecedenti;
  factory _StatoVoto.fromJson(Map<String, dynamic> json) => _$StatoVotoFromJson(json);

@override final  Tornata? tornata;
@override final  String? mioVoto;
 final  List<CandidatoVoto> _candidati;
@override@JsonKey() List<CandidatoVoto> get candidati {
  if (_candidati is EqualUnmodifiableListView) return _candidati;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_candidati);
}

 final  List<VincitorePrecedente>? _vincitoriPrecedenti;
@override List<VincitorePrecedente>? get vincitoriPrecedenti {
  final value = _vincitoriPrecedenti;
  if (value == null) return null;
  if (_vincitoriPrecedenti is EqualUnmodifiableListView) return _vincitoriPrecedenti;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}


/// Create a copy of StatoVoto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$StatoVotoCopyWith<_StatoVoto> get copyWith => __$StatoVotoCopyWithImpl<_StatoVoto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$StatoVotoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _StatoVoto&&(identical(other.tornata, tornata) || other.tornata == tornata)&&(identical(other.mioVoto, mioVoto) || other.mioVoto == mioVoto)&&const DeepCollectionEquality().equals(other.candidati, _candidati)&&const DeepCollectionEquality().equals(other.vincitoriPrecedenti, _vincitoriPrecedenti));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,tornata,mioVoto,const DeepCollectionEquality().hash(_candidati),const DeepCollectionEquality().hash(_vincitoriPrecedenti));
}

@override
String toString() {
    return 'StatoVoto(tornata: $tornata, mioVoto: $mioVoto, candidati: $candidati, vincitoriPrecedenti: $vincitoriPrecedenti)';
}


}

/// @nodoc
abstract mixin class _$StatoVotoCopyWith<$Res> implements $StatoVotoCopyWith<$Res> {
  factory _$StatoVotoCopyWith(_StatoVoto value, $Res Function(_StatoVoto) _then) = __$StatoVotoCopyWithImpl;
@override @useResult
$Res call({
 Tornata? tornata, String? mioVoto, List<CandidatoVoto> candidati, List<VincitorePrecedente>? vincitoriPrecedenti
});


@override $TornataCopyWith<$Res>? get tornata;

}
/// @nodoc
class __$StatoVotoCopyWithImpl<$Res>
    implements _$StatoVotoCopyWith<$Res> {
  __$StatoVotoCopyWithImpl(this._self, this._then);

  final _StatoVoto _self;
  final $Res Function(_StatoVoto) _then;

/// Create a copy of StatoVoto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? tornata = freezed,Object? mioVoto = freezed,Object? candidati = null,Object? vincitoriPrecedenti = freezed,}) {
  return _then(_StatoVoto(
tornata: freezed == tornata ? _self.tornata : tornata // ignore: cast_nullable_to_non_nullable
as Tornata?,mioVoto: freezed == mioVoto ? _self.mioVoto : mioVoto // ignore: cast_nullable_to_non_nullable
as String?,candidati: null == candidati ? _self._candidati : candidati // ignore: cast_nullable_to_non_nullable
as List<CandidatoVoto>,vincitoriPrecedenti: freezed == vincitoriPrecedenti ? _self._vincitoriPrecedenti : vincitoriPrecedenti // ignore: cast_nullable_to_non_nullable
as List<VincitorePrecedente>?,
  ));
}

/// Create a copy of StatoVoto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$TornataCopyWith<$Res>? get tornata {
    if (_self.tornata == null) {
    return null;
  }

  return $TornataCopyWith<$Res>(_self.tornata!, (value) {
    return _then(_self.copyWith(tornata: value));
  });
}
}


/// @nodoc
mixin _$CandidatoRisultato {

 String get nome; num get percentuale; List<CampioneVoto> get campioni;
/// Create a copy of CandidatoRisultato
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CandidatoRisultatoCopyWith<CandidatoRisultato> get copyWith => _$CandidatoRisultatoCopyWithImpl<CandidatoRisultato>(this as CandidatoRisultato, _$identity);

  /// Serializes this CandidatoRisultato to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as CandidatoRisultato;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CandidatoRisultato&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.percentuale, _this.percentuale) || other.percentuale == _this.percentuale)&&const DeepCollectionEquality().equals(other.campioni, _this.campioni));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as CandidatoRisultato;
  return Object.hash(runtimeType,_this.nome,_this.percentuale,const DeepCollectionEquality().hash(_this.campioni));
}

@override
String toString() {
  final _this = this as CandidatoRisultato;
  return 'CandidatoRisultato(nome: ${_this.nome}, percentuale: ${_this.percentuale}, campioni: ${_this.campioni})';
}


}

/// @nodoc
abstract mixin class $CandidatoRisultatoCopyWith<$Res>  {
  factory $CandidatoRisultatoCopyWith(CandidatoRisultato value, $Res Function(CandidatoRisultato) _then) = _$CandidatoRisultatoCopyWithImpl;
@useResult
$Res call({
 String nome, num percentuale, List<CampioneVoto> campioni
});




}
/// @nodoc
class _$CandidatoRisultatoCopyWithImpl<$Res>
    implements $CandidatoRisultatoCopyWith<$Res> {
  _$CandidatoRisultatoCopyWithImpl(this._self, this._then);

  final CandidatoRisultato _self;
  final $Res Function(CandidatoRisultato) _then;

/// Create a copy of CandidatoRisultato
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? nome = null,Object? percentuale = null,Object? campioni = null,}) {
  return _then(CandidatoRisultato(
nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,percentuale: null == percentuale ? _self.percentuale : percentuale // ignore: cast_nullable_to_non_nullable
as num,campioni: null == campioni ? _self.campioni : campioni // ignore: cast_nullable_to_non_nullable
as List<CampioneVoto>,
  ));
}

}


/// Adds pattern-matching-related methods to [CandidatoRisultato].
extension CandidatoRisultatoPatterns on CandidatoRisultato {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CandidatoRisultato value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CandidatoRisultato() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CandidatoRisultato value)  $default,){
final _that = this;
switch (_that) {
case _CandidatoRisultato():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CandidatoRisultato value)?  $default,){
final _that = this;
switch (_that) {
case _CandidatoRisultato() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String nome,  num percentuale,  List<CampioneVoto> campioni)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CandidatoRisultato() when $default != null:
return $default(_that.nome,_that.percentuale,_that.campioni);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String nome,  num percentuale,  List<CampioneVoto> campioni)  $default,) {final _that = this;
switch (_that) {
case _CandidatoRisultato():
return $default(_that.nome,_that.percentuale,_that.campioni);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String nome,  num percentuale,  List<CampioneVoto> campioni)?  $default,) {final _that = this;
switch (_that) {
case _CandidatoRisultato() when $default != null:
return $default(_that.nome,_that.percentuale,_that.campioni);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CandidatoRisultato implements CandidatoRisultato {
  const _CandidatoRisultato({required this.nome, required this.percentuale,  List<CampioneVoto> campioni = const <CampioneVoto>[]}): _campioni = campioni;
  factory _CandidatoRisultato.fromJson(Map<String, dynamic> json) => _$CandidatoRisultatoFromJson(json);

@override final  String nome;
@override final  num percentuale;
 final  List<CampioneVoto> _campioni;
@override@JsonKey() List<CampioneVoto> get campioni {
  if (_campioni is EqualUnmodifiableListView) return _campioni;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_campioni);
}


/// Create a copy of CandidatoRisultato
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CandidatoRisultatoCopyWith<_CandidatoRisultato> get copyWith => __$CandidatoRisultatoCopyWithImpl<_CandidatoRisultato>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CandidatoRisultatoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _CandidatoRisultato&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.percentuale, percentuale) || other.percentuale == percentuale)&&const DeepCollectionEquality().equals(other.campioni, _campioni));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,nome,percentuale,const DeepCollectionEquality().hash(_campioni));
}

@override
String toString() {
    return 'CandidatoRisultato(nome: $nome, percentuale: $percentuale, campioni: $campioni)';
}


}

/// @nodoc
abstract mixin class _$CandidatoRisultatoCopyWith<$Res> implements $CandidatoRisultatoCopyWith<$Res> {
  factory _$CandidatoRisultatoCopyWith(_CandidatoRisultato value, $Res Function(_CandidatoRisultato) _then) = __$CandidatoRisultatoCopyWithImpl;
@override @useResult
$Res call({
 String nome, num percentuale, List<CampioneVoto> campioni
});




}
/// @nodoc
class __$CandidatoRisultatoCopyWithImpl<$Res>
    implements _$CandidatoRisultatoCopyWith<$Res> {
  __$CandidatoRisultatoCopyWithImpl(this._self, this._then);

  final _CandidatoRisultato _self;
  final $Res Function(_CandidatoRisultato) _then;

/// Create a copy of CandidatoRisultato
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? nome = null,Object? percentuale = null,Object? campioni = null,}) {
  return _then(_CandidatoRisultato(
nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,percentuale: null == percentuale ? _self.percentuale : percentuale // ignore: cast_nullable_to_non_nullable
as num,campioni: null == campioni ? _self._campioni : campioni // ignore: cast_nullable_to_non_nullable
as List<CampioneVoto>,
  ));
}


}


/// @nodoc
mixin _$RisultatoRecente {

 String? get chiusaIl; List<CandidatoRisultato> get candidati;
/// Create a copy of RisultatoRecente
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RisultatoRecenteCopyWith<RisultatoRecente> get copyWith => _$RisultatoRecenteCopyWithImpl<RisultatoRecente>(this as RisultatoRecente, _$identity);

  /// Serializes this RisultatoRecente to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as RisultatoRecente;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RisultatoRecente&&(identical(other.chiusaIl, _this.chiusaIl) || other.chiusaIl == _this.chiusaIl)&&const DeepCollectionEquality().equals(other.candidati, _this.candidati));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as RisultatoRecente;
  return Object.hash(runtimeType,_this.chiusaIl,const DeepCollectionEquality().hash(_this.candidati));
}

@override
String toString() {
  final _this = this as RisultatoRecente;
  return 'RisultatoRecente(chiusaIl: ${_this.chiusaIl}, candidati: ${_this.candidati})';
}


}

/// @nodoc
abstract mixin class $RisultatoRecenteCopyWith<$Res>  {
  factory $RisultatoRecenteCopyWith(RisultatoRecente value, $Res Function(RisultatoRecente) _then) = _$RisultatoRecenteCopyWithImpl;
@useResult
$Res call({
 String? chiusaIl, List<CandidatoRisultato> candidati
});




}
/// @nodoc
class _$RisultatoRecenteCopyWithImpl<$Res>
    implements $RisultatoRecenteCopyWith<$Res> {
  _$RisultatoRecenteCopyWithImpl(this._self, this._then);

  final RisultatoRecente _self;
  final $Res Function(RisultatoRecente) _then;

/// Create a copy of RisultatoRecente
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? chiusaIl = freezed,Object? candidati = null,}) {
  return _then(RisultatoRecente(
chiusaIl: freezed == chiusaIl ? _self.chiusaIl : chiusaIl // ignore: cast_nullable_to_non_nullable
as String?,candidati: null == candidati ? _self.candidati : candidati // ignore: cast_nullable_to_non_nullable
as List<CandidatoRisultato>,
  ));
}

}


/// Adds pattern-matching-related methods to [RisultatoRecente].
extension RisultatoRecentePatterns on RisultatoRecente {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _RisultatoRecente value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _RisultatoRecente() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _RisultatoRecente value)  $default,){
final _that = this;
switch (_that) {
case _RisultatoRecente():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _RisultatoRecente value)?  $default,){
final _that = this;
switch (_that) {
case _RisultatoRecente() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? chiusaIl,  List<CandidatoRisultato> candidati)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _RisultatoRecente() when $default != null:
return $default(_that.chiusaIl,_that.candidati);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? chiusaIl,  List<CandidatoRisultato> candidati)  $default,) {final _that = this;
switch (_that) {
case _RisultatoRecente():
return $default(_that.chiusaIl,_that.candidati);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? chiusaIl,  List<CandidatoRisultato> candidati)?  $default,) {final _that = this;
switch (_that) {
case _RisultatoRecente() when $default != null:
return $default(_that.chiusaIl,_that.candidati);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _RisultatoRecente implements RisultatoRecente {
  const _RisultatoRecente({this.chiusaIl,  List<CandidatoRisultato> candidati = const <CandidatoRisultato>[]}): _candidati = candidati;
  factory _RisultatoRecente.fromJson(Map<String, dynamic> json) => _$RisultatoRecenteFromJson(json);

@override final  String? chiusaIl;
 final  List<CandidatoRisultato> _candidati;
@override@JsonKey() List<CandidatoRisultato> get candidati {
  if (_candidati is EqualUnmodifiableListView) return _candidati;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_candidati);
}


/// Create a copy of RisultatoRecente
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RisultatoRecenteCopyWith<_RisultatoRecente> get copyWith => __$RisultatoRecenteCopyWithImpl<_RisultatoRecente>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$RisultatoRecenteToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _RisultatoRecente&&(identical(other.chiusaIl, chiusaIl) || other.chiusaIl == chiusaIl)&&const DeepCollectionEquality().equals(other.candidati, _candidati));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,chiusaIl,const DeepCollectionEquality().hash(_candidati));
}

@override
String toString() {
    return 'RisultatoRecente(chiusaIl: $chiusaIl, candidati: $candidati)';
}


}

/// @nodoc
abstract mixin class _$RisultatoRecenteCopyWith<$Res> implements $RisultatoRecenteCopyWith<$Res> {
  factory _$RisultatoRecenteCopyWith(_RisultatoRecente value, $Res Function(_RisultatoRecente) _then) = __$RisultatoRecenteCopyWithImpl;
@override @useResult
$Res call({
 String? chiusaIl, List<CandidatoRisultato> candidati
});




}
/// @nodoc
class __$RisultatoRecenteCopyWithImpl<$Res>
    implements _$RisultatoRecenteCopyWith<$Res> {
  __$RisultatoRecenteCopyWithImpl(this._self, this._then);

  final _RisultatoRecente _self;
  final $Res Function(_RisultatoRecente) _then;

/// Create a copy of RisultatoRecente
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? chiusaIl = freezed,Object? candidati = null,}) {
  return _then(_RisultatoRecente(
chiusaIl: freezed == chiusaIl ? _self.chiusaIl : chiusaIl // ignore: cast_nullable_to_non_nullable
as String?,candidati: null == candidati ? _self._candidati : candidati // ignore: cast_nullable_to_non_nullable
as List<CandidatoRisultato>,
  ));
}


}


/// @nodoc
mixin _$VotoHome {

 bool get votoAperto; RisultatoRecente? get risultatoRecente;
/// Create a copy of VotoHome
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$VotoHomeCopyWith<VotoHome> get copyWith => _$VotoHomeCopyWithImpl<VotoHome>(this as VotoHome, _$identity);

  /// Serializes this VotoHome to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as VotoHome;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is VotoHome&&(identical(other.votoAperto, _this.votoAperto) || other.votoAperto == _this.votoAperto)&&(identical(other.risultatoRecente, _this.risultatoRecente) || other.risultatoRecente == _this.risultatoRecente));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as VotoHome;
  return Object.hash(runtimeType,_this.votoAperto,_this.risultatoRecente);
}

@override
String toString() {
  final _this = this as VotoHome;
  return 'VotoHome(votoAperto: ${_this.votoAperto}, risultatoRecente: ${_this.risultatoRecente})';
}


}

/// @nodoc
abstract mixin class $VotoHomeCopyWith<$Res>  {
  factory $VotoHomeCopyWith(VotoHome value, $Res Function(VotoHome) _then) = _$VotoHomeCopyWithImpl;
@useResult
$Res call({
 bool votoAperto, RisultatoRecente? risultatoRecente
});


$RisultatoRecenteCopyWith<$Res>? get risultatoRecente;

}
/// @nodoc
class _$VotoHomeCopyWithImpl<$Res>
    implements $VotoHomeCopyWith<$Res> {
  _$VotoHomeCopyWithImpl(this._self, this._then);

  final VotoHome _self;
  final $Res Function(VotoHome) _then;

/// Create a copy of VotoHome
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? votoAperto = null,Object? risultatoRecente = freezed,}) {
  return _then(VotoHome(
votoAperto: null == votoAperto ? _self.votoAperto : votoAperto // ignore: cast_nullable_to_non_nullable
as bool,risultatoRecente: freezed == risultatoRecente ? _self.risultatoRecente : risultatoRecente // ignore: cast_nullable_to_non_nullable
as RisultatoRecente?,
  ));
}
/// Create a copy of VotoHome
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$RisultatoRecenteCopyWith<$Res>? get risultatoRecente {
    if (_self.risultatoRecente == null) {
    return null;
  }

  return $RisultatoRecenteCopyWith<$Res>(_self.risultatoRecente!, (value) {
    return _then(_self.copyWith(risultatoRecente: value));
  });
}
}


/// Adds pattern-matching-related methods to [VotoHome].
extension VotoHomePatterns on VotoHome {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _VotoHome value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _VotoHome() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _VotoHome value)  $default,){
final _that = this;
switch (_that) {
case _VotoHome():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _VotoHome value)?  $default,){
final _that = this;
switch (_that) {
case _VotoHome() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( bool votoAperto,  RisultatoRecente? risultatoRecente)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _VotoHome() when $default != null:
return $default(_that.votoAperto,_that.risultatoRecente);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( bool votoAperto,  RisultatoRecente? risultatoRecente)  $default,) {final _that = this;
switch (_that) {
case _VotoHome():
return $default(_that.votoAperto,_that.risultatoRecente);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( bool votoAperto,  RisultatoRecente? risultatoRecente)?  $default,) {final _that = this;
switch (_that) {
case _VotoHome() when $default != null:
return $default(_that.votoAperto,_that.risultatoRecente);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _VotoHome implements VotoHome {
  const _VotoHome({this.votoAperto = false, this.risultatoRecente});
  factory _VotoHome.fromJson(Map<String, dynamic> json) => _$VotoHomeFromJson(json);

@override@JsonKey() final  bool votoAperto;
@override final  RisultatoRecente? risultatoRecente;

/// Create a copy of VotoHome
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$VotoHomeCopyWith<_VotoHome> get copyWith => __$VotoHomeCopyWithImpl<_VotoHome>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$VotoHomeToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _VotoHome&&(identical(other.votoAperto, votoAperto) || other.votoAperto == votoAperto)&&(identical(other.risultatoRecente, risultatoRecente) || other.risultatoRecente == risultatoRecente));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,votoAperto,risultatoRecente);
}

@override
String toString() {
    return 'VotoHome(votoAperto: $votoAperto, risultatoRecente: $risultatoRecente)';
}


}

/// @nodoc
abstract mixin class _$VotoHomeCopyWith<$Res> implements $VotoHomeCopyWith<$Res> {
  factory _$VotoHomeCopyWith(_VotoHome value, $Res Function(_VotoHome) _then) = __$VotoHomeCopyWithImpl;
@override @useResult
$Res call({
 bool votoAperto, RisultatoRecente? risultatoRecente
});


@override $RisultatoRecenteCopyWith<$Res>? get risultatoRecente;

}
/// @nodoc
class __$VotoHomeCopyWithImpl<$Res>
    implements _$VotoHomeCopyWith<$Res> {
  __$VotoHomeCopyWithImpl(this._self, this._then);

  final _VotoHome _self;
  final $Res Function(_VotoHome) _then;

/// Create a copy of VotoHome
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? votoAperto = null,Object? risultatoRecente = freezed,}) {
  return _then(_VotoHome(
votoAperto: null == votoAperto ? _self.votoAperto : votoAperto // ignore: cast_nullable_to_non_nullable
as bool,risultatoRecente: freezed == risultatoRecente ? _self.risultatoRecente : risultatoRecente // ignore: cast_nullable_to_non_nullable
as RisultatoRecente?,
  ));
}

/// Create a copy of VotoHome
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$RisultatoRecenteCopyWith<$Res>? get risultatoRecente {
    if (_self.risultatoRecente == null) {
    return null;
  }

  return $RisultatoRecenteCopyWith<$Res>(_self.risultatoRecente!, (value) {
    return _then(_self.copyWith(risultatoRecente: value));
  });
}
}

// dart format on

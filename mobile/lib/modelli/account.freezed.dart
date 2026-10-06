// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'account.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$PersonaSalvata {

 String get nome; String? get cognome;/// `donna`, `uomo`, `non_binario`, `altro`, `non_dice`.
 String get genere; String? get genereAltro; bool get trans; String get nascita;
/// Create a copy of PersonaSalvata
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PersonaSalvataCopyWith<PersonaSalvata> get copyWith => _$PersonaSalvataCopyWithImpl<PersonaSalvata>(this as PersonaSalvata, _$identity);

  /// Serializes this PersonaSalvata to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as PersonaSalvata;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PersonaSalvata&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.cognome, _this.cognome) || other.cognome == _this.cognome)&&(identical(other.genere, _this.genere) || other.genere == _this.genere)&&(identical(other.genereAltro, _this.genereAltro) || other.genereAltro == _this.genereAltro)&&(identical(other.trans, _this.trans) || other.trans == _this.trans)&&(identical(other.nascita, _this.nascita) || other.nascita == _this.nascita));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as PersonaSalvata;
  return Object.hash(runtimeType,_this.nome,_this.cognome,_this.genere,_this.genereAltro,_this.trans,_this.nascita);
}

@override
String toString() {
  final _this = this as PersonaSalvata;
  return 'PersonaSalvata(nome: ${_this.nome}, cognome: ${_this.cognome}, genere: ${_this.genere}, genereAltro: ${_this.genereAltro}, trans: ${_this.trans}, nascita: ${_this.nascita})';
}


}

/// @nodoc
abstract mixin class $PersonaSalvataCopyWith<$Res>  {
  factory $PersonaSalvataCopyWith(PersonaSalvata value, $Res Function(PersonaSalvata) _then) = _$PersonaSalvataCopyWithImpl;
@useResult
$Res call({
 String nome, String? cognome, String genere, String? genereAltro, bool trans, String nascita
});




}
/// @nodoc
class _$PersonaSalvataCopyWithImpl<$Res>
    implements $PersonaSalvataCopyWith<$Res> {
  _$PersonaSalvataCopyWithImpl(this._self, this._then);

  final PersonaSalvata _self;
  final $Res Function(PersonaSalvata) _then;

/// Create a copy of PersonaSalvata
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? nome = null,Object? cognome = freezed,Object? genere = null,Object? genereAltro = freezed,Object? trans = null,Object? nascita = null,}) {
  return _then(PersonaSalvata(
nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,cognome: freezed == cognome ? _self.cognome : cognome // ignore: cast_nullable_to_non_nullable
as String?,genere: null == genere ? _self.genere : genere // ignore: cast_nullable_to_non_nullable
as String,genereAltro: freezed == genereAltro ? _self.genereAltro : genereAltro // ignore: cast_nullable_to_non_nullable
as String?,trans: null == trans ? _self.trans : trans // ignore: cast_nullable_to_non_nullable
as bool,nascita: null == nascita ? _self.nascita : nascita // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [PersonaSalvata].
extension PersonaSalvataPatterns on PersonaSalvata {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PersonaSalvata value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PersonaSalvata() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PersonaSalvata value)  $default,){
final _that = this;
switch (_that) {
case _PersonaSalvata():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PersonaSalvata value)?  $default,){
final _that = this;
switch (_that) {
case _PersonaSalvata() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String nome,  String? cognome,  String genere,  String? genereAltro,  bool trans,  String nascita)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PersonaSalvata() when $default != null:
return $default(_that.nome,_that.cognome,_that.genere,_that.genereAltro,_that.trans,_that.nascita);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String nome,  String? cognome,  String genere,  String? genereAltro,  bool trans,  String nascita)  $default,) {final _that = this;
switch (_that) {
case _PersonaSalvata():
return $default(_that.nome,_that.cognome,_that.genere,_that.genereAltro,_that.trans,_that.nascita);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String nome,  String? cognome,  String genere,  String? genereAltro,  bool trans,  String nascita)?  $default,) {final _that = this;
switch (_that) {
case _PersonaSalvata() when $default != null:
return $default(_that.nome,_that.cognome,_that.genere,_that.genereAltro,_that.trans,_that.nascita);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _PersonaSalvata implements PersonaSalvata {
  const _PersonaSalvata({required this.nome, this.cognome, required this.genere, this.genereAltro, this.trans = false, required this.nascita});
  factory _PersonaSalvata.fromJson(Map<String, dynamic> json) => _$PersonaSalvataFromJson(json);

@override final  String nome;
@override final  String? cognome;
/// `donna`, `uomo`, `non_binario`, `altro`, `non_dice`.
@override final  String genere;
@override final  String? genereAltro;
@override@JsonKey() final  bool trans;
@override final  String nascita;

/// Create a copy of PersonaSalvata
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PersonaSalvataCopyWith<_PersonaSalvata> get copyWith => __$PersonaSalvataCopyWithImpl<_PersonaSalvata>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PersonaSalvataToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _PersonaSalvata&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.cognome, cognome) || other.cognome == cognome)&&(identical(other.genere, genere) || other.genere == genere)&&(identical(other.genereAltro, genereAltro) || other.genereAltro == genereAltro)&&(identical(other.trans, trans) || other.trans == trans)&&(identical(other.nascita, nascita) || other.nascita == nascita));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,nome,cognome,genere,genereAltro,trans,nascita);
}

@override
String toString() {
    return 'PersonaSalvata(nome: $nome, cognome: $cognome, genere: $genere, genereAltro: $genereAltro, trans: $trans, nascita: $nascita)';
}


}

/// @nodoc
abstract mixin class _$PersonaSalvataCopyWith<$Res> implements $PersonaSalvataCopyWith<$Res> {
  factory _$PersonaSalvataCopyWith(_PersonaSalvata value, $Res Function(_PersonaSalvata) _then) = __$PersonaSalvataCopyWithImpl;
@override @useResult
$Res call({
 String nome, String? cognome, String genere, String? genereAltro, bool trans, String nascita
});




}
/// @nodoc
class __$PersonaSalvataCopyWithImpl<$Res>
    implements _$PersonaSalvataCopyWith<$Res> {
  __$PersonaSalvataCopyWithImpl(this._self, this._then);

  final _PersonaSalvata _self;
  final $Res Function(_PersonaSalvata) _then;

/// Create a copy of PersonaSalvata
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? nome = null,Object? cognome = freezed,Object? genere = null,Object? genereAltro = freezed,Object? trans = null,Object? nascita = null,}) {
  return _then(_PersonaSalvata(
nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,cognome: freezed == cognome ? _self.cognome : cognome // ignore: cast_nullable_to_non_nullable
as String?,genere: null == genere ? _self.genere : genere // ignore: cast_nullable_to_non_nullable
as String,genereAltro: freezed == genereAltro ? _self.genereAltro : genereAltro // ignore: cast_nullable_to_non_nullable
as String?,trans: null == trans ? _self.trans : trans // ignore: cast_nullable_to_non_nullable
as bool,nascita: null == nascita ? _self.nascita : nascita // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$Condivisioni {

 int get verificate; int get premi; int get prossimoTra; int get iscrizioni; int get soglia; int get creditiIscrizione;
/// Create a copy of Condivisioni
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CondivisioniCopyWith<Condivisioni> get copyWith => _$CondivisioniCopyWithImpl<Condivisioni>(this as Condivisioni, _$identity);

  /// Serializes this Condivisioni to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Condivisioni;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Condivisioni&&(identical(other.verificate, _this.verificate) || other.verificate == _this.verificate)&&(identical(other.premi, _this.premi) || other.premi == _this.premi)&&(identical(other.prossimoTra, _this.prossimoTra) || other.prossimoTra == _this.prossimoTra)&&(identical(other.iscrizioni, _this.iscrizioni) || other.iscrizioni == _this.iscrizioni)&&(identical(other.soglia, _this.soglia) || other.soglia == _this.soglia)&&(identical(other.creditiIscrizione, _this.creditiIscrizione) || other.creditiIscrizione == _this.creditiIscrizione));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Condivisioni;
  return Object.hash(runtimeType,_this.verificate,_this.premi,_this.prossimoTra,_this.iscrizioni,_this.soglia,_this.creditiIscrizione);
}

@override
String toString() {
  final _this = this as Condivisioni;
  return 'Condivisioni(verificate: ${_this.verificate}, premi: ${_this.premi}, prossimoTra: ${_this.prossimoTra}, iscrizioni: ${_this.iscrizioni}, soglia: ${_this.soglia}, creditiIscrizione: ${_this.creditiIscrizione})';
}


}

/// @nodoc
abstract mixin class $CondivisioniCopyWith<$Res>  {
  factory $CondivisioniCopyWith(Condivisioni value, $Res Function(Condivisioni) _then) = _$CondivisioniCopyWithImpl;
@useResult
$Res call({
 int verificate, int premi, int prossimoTra, int iscrizioni, int soglia, int creditiIscrizione
});




}
/// @nodoc
class _$CondivisioniCopyWithImpl<$Res>
    implements $CondivisioniCopyWith<$Res> {
  _$CondivisioniCopyWithImpl(this._self, this._then);

  final Condivisioni _self;
  final $Res Function(Condivisioni) _then;

/// Create a copy of Condivisioni
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? verificate = null,Object? premi = null,Object? prossimoTra = null,Object? iscrizioni = null,Object? soglia = null,Object? creditiIscrizione = null,}) {
  return _then(Condivisioni(
verificate: null == verificate ? _self.verificate : verificate // ignore: cast_nullable_to_non_nullable
as int,premi: null == premi ? _self.premi : premi // ignore: cast_nullable_to_non_nullable
as int,prossimoTra: null == prossimoTra ? _self.prossimoTra : prossimoTra // ignore: cast_nullable_to_non_nullable
as int,iscrizioni: null == iscrizioni ? _self.iscrizioni : iscrizioni // ignore: cast_nullable_to_non_nullable
as int,soglia: null == soglia ? _self.soglia : soglia // ignore: cast_nullable_to_non_nullable
as int,creditiIscrizione: null == creditiIscrizione ? _self.creditiIscrizione : creditiIscrizione // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [Condivisioni].
extension CondivisioniPatterns on Condivisioni {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Condivisioni value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Condivisioni() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Condivisioni value)  $default,){
final _that = this;
switch (_that) {
case _Condivisioni():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Condivisioni value)?  $default,){
final _that = this;
switch (_that) {
case _Condivisioni() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int verificate,  int premi,  int prossimoTra,  int iscrizioni,  int soglia,  int creditiIscrizione)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Condivisioni() when $default != null:
return $default(_that.verificate,_that.premi,_that.prossimoTra,_that.iscrizioni,_that.soglia,_that.creditiIscrizione);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int verificate,  int premi,  int prossimoTra,  int iscrizioni,  int soglia,  int creditiIscrizione)  $default,) {final _that = this;
switch (_that) {
case _Condivisioni():
return $default(_that.verificate,_that.premi,_that.prossimoTra,_that.iscrizioni,_that.soglia,_that.creditiIscrizione);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int verificate,  int premi,  int prossimoTra,  int iscrizioni,  int soglia,  int creditiIscrizione)?  $default,) {final _that = this;
switch (_that) {
case _Condivisioni() when $default != null:
return $default(_that.verificate,_that.premi,_that.prossimoTra,_that.iscrizioni,_that.soglia,_that.creditiIscrizione);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Condivisioni implements Condivisioni {
  const _Condivisioni({this.verificate = 0, this.premi = 0, this.prossimoTra = 0, this.iscrizioni = 0, this.soglia = 5, this.creditiIscrizione = 5});
  factory _Condivisioni.fromJson(Map<String, dynamic> json) => _$CondivisioniFromJson(json);

@override@JsonKey() final  int verificate;
@override@JsonKey() final  int premi;
@override@JsonKey() final  int prossimoTra;
@override@JsonKey() final  int iscrizioni;
@override@JsonKey() final  int soglia;
@override@JsonKey() final  int creditiIscrizione;

/// Create a copy of Condivisioni
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CondivisioniCopyWith<_Condivisioni> get copyWith => __$CondivisioniCopyWithImpl<_Condivisioni>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CondivisioniToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Condivisioni&&(identical(other.verificate, verificate) || other.verificate == verificate)&&(identical(other.premi, premi) || other.premi == premi)&&(identical(other.prossimoTra, prossimoTra) || other.prossimoTra == prossimoTra)&&(identical(other.iscrizioni, iscrizioni) || other.iscrizioni == iscrizioni)&&(identical(other.soglia, soglia) || other.soglia == soglia)&&(identical(other.creditiIscrizione, creditiIscrizione) || other.creditiIscrizione == creditiIscrizione));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,verificate,premi,prossimoTra,iscrizioni,soglia,creditiIscrizione);
}

@override
String toString() {
    return 'Condivisioni(verificate: $verificate, premi: $premi, prossimoTra: $prossimoTra, iscrizioni: $iscrizioni, soglia: $soglia, creditiIscrizione: $creditiIscrizione)';
}


}

/// @nodoc
abstract mixin class _$CondivisioniCopyWith<$Res> implements $CondivisioniCopyWith<$Res> {
  factory _$CondivisioniCopyWith(_Condivisioni value, $Res Function(_Condivisioni) _then) = __$CondivisioniCopyWithImpl;
@override @useResult
$Res call({
 int verificate, int premi, int prossimoTra, int iscrizioni, int soglia, int creditiIscrizione
});




}
/// @nodoc
class __$CondivisioniCopyWithImpl<$Res>
    implements _$CondivisioniCopyWith<$Res> {
  __$CondivisioniCopyWithImpl(this._self, this._then);

  final _Condivisioni _self;
  final $Res Function(_Condivisioni) _then;

/// Create a copy of Condivisioni
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? verificate = null,Object? premi = null,Object? prossimoTra = null,Object? iscrizioni = null,Object? soglia = null,Object? creditiIscrizione = null,}) {
  return _then(_Condivisioni(
verificate: null == verificate ? _self.verificate : verificate // ignore: cast_nullable_to_non_nullable
as int,premi: null == premi ? _self.premi : premi // ignore: cast_nullable_to_non_nullable
as int,prossimoTra: null == prossimoTra ? _self.prossimoTra : prossimoTra // ignore: cast_nullable_to_non_nullable
as int,iscrizioni: null == iscrizioni ? _self.iscrizioni : iscrizioni // ignore: cast_nullable_to_non_nullable
as int,soglia: null == soglia ? _self.soglia : soglia // ignore: cast_nullable_to_non_nullable
as int,creditiIscrizione: null == creditiIscrizione ? _self.creditiIscrizione : creditiIscrizione // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$PosizioneAttuale {

 String? get paese; String? get citta; String? get fonte; String? get il;
/// Create a copy of PosizioneAttuale
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PosizioneAttualeCopyWith<PosizioneAttuale> get copyWith => _$PosizioneAttualeCopyWithImpl<PosizioneAttuale>(this as PosizioneAttuale, _$identity);

  /// Serializes this PosizioneAttuale to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as PosizioneAttuale;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PosizioneAttuale&&(identical(other.paese, _this.paese) || other.paese == _this.paese)&&(identical(other.citta, _this.citta) || other.citta == _this.citta)&&(identical(other.fonte, _this.fonte) || other.fonte == _this.fonte)&&(identical(other.il, _this.il) || other.il == _this.il));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as PosizioneAttuale;
  return Object.hash(runtimeType,_this.paese,_this.citta,_this.fonte,_this.il);
}

@override
String toString() {
  final _this = this as PosizioneAttuale;
  return 'PosizioneAttuale(paese: ${_this.paese}, citta: ${_this.citta}, fonte: ${_this.fonte}, il: ${_this.il})';
}


}

/// @nodoc
abstract mixin class $PosizioneAttualeCopyWith<$Res>  {
  factory $PosizioneAttualeCopyWith(PosizioneAttuale value, $Res Function(PosizioneAttuale) _then) = _$PosizioneAttualeCopyWithImpl;
@useResult
$Res call({
 String? paese, String? citta, String? fonte, String? il
});




}
/// @nodoc
class _$PosizioneAttualeCopyWithImpl<$Res>
    implements $PosizioneAttualeCopyWith<$Res> {
  _$PosizioneAttualeCopyWithImpl(this._self, this._then);

  final PosizioneAttuale _self;
  final $Res Function(PosizioneAttuale) _then;

/// Create a copy of PosizioneAttuale
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? paese = freezed,Object? citta = freezed,Object? fonte = freezed,Object? il = freezed,}) {
  return _then(PosizioneAttuale(
paese: freezed == paese ? _self.paese : paese // ignore: cast_nullable_to_non_nullable
as String?,citta: freezed == citta ? _self.citta : citta // ignore: cast_nullable_to_non_nullable
as String?,fonte: freezed == fonte ? _self.fonte : fonte // ignore: cast_nullable_to_non_nullable
as String?,il: freezed == il ? _self.il : il // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [PosizioneAttuale].
extension PosizioneAttualePatterns on PosizioneAttuale {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PosizioneAttuale value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PosizioneAttuale() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PosizioneAttuale value)  $default,){
final _that = this;
switch (_that) {
case _PosizioneAttuale():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PosizioneAttuale value)?  $default,){
final _that = this;
switch (_that) {
case _PosizioneAttuale() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? paese,  String? citta,  String? fonte,  String? il)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PosizioneAttuale() when $default != null:
return $default(_that.paese,_that.citta,_that.fonte,_that.il);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? paese,  String? citta,  String? fonte,  String? il)  $default,) {final _that = this;
switch (_that) {
case _PosizioneAttuale():
return $default(_that.paese,_that.citta,_that.fonte,_that.il);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? paese,  String? citta,  String? fonte,  String? il)?  $default,) {final _that = this;
switch (_that) {
case _PosizioneAttuale() when $default != null:
return $default(_that.paese,_that.citta,_that.fonte,_that.il);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _PosizioneAttuale implements PosizioneAttuale {
  const _PosizioneAttuale({this.paese, this.citta, this.fonte, this.il});
  factory _PosizioneAttuale.fromJson(Map<String, dynamic> json) => _$PosizioneAttualeFromJson(json);

@override final  String? paese;
@override final  String? citta;
@override final  String? fonte;
@override final  String? il;

/// Create a copy of PosizioneAttuale
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PosizioneAttualeCopyWith<_PosizioneAttuale> get copyWith => __$PosizioneAttualeCopyWithImpl<_PosizioneAttuale>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PosizioneAttualeToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _PosizioneAttuale&&(identical(other.paese, paese) || other.paese == paese)&&(identical(other.citta, citta) || other.citta == citta)&&(identical(other.fonte, fonte) || other.fonte == fonte)&&(identical(other.il, il) || other.il == il));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,paese,citta,fonte,il);
}

@override
String toString() {
    return 'PosizioneAttuale(paese: $paese, citta: $citta, fonte: $fonte, il: $il)';
}


}

/// @nodoc
abstract mixin class _$PosizioneAttualeCopyWith<$Res> implements $PosizioneAttualeCopyWith<$Res> {
  factory _$PosizioneAttualeCopyWith(_PosizioneAttuale value, $Res Function(_PosizioneAttuale) _then) = __$PosizioneAttualeCopyWithImpl;
@override @useResult
$Res call({
 String? paese, String? citta, String? fonte, String? il
});




}
/// @nodoc
class __$PosizioneAttualeCopyWithImpl<$Res>
    implements _$PosizioneAttualeCopyWith<$Res> {
  __$PosizioneAttualeCopyWithImpl(this._self, this._then);

  final _PosizioneAttuale _self;
  final $Res Function(_PosizioneAttuale) _then;

/// Create a copy of PosizioneAttuale
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? paese = freezed,Object? citta = freezed,Object? fonte = freezed,Object? il = freezed,}) {
  return _then(_PosizioneAttuale(
paese: freezed == paese ? _self.paese : paese // ignore: cast_nullable_to_non_nullable
as String?,citta: freezed == citta ? _self.citta : citta // ignore: cast_nullable_to_non_nullable
as String?,fonte: freezed == fonte ? _self.fonte : fonte // ignore: cast_nullable_to_non_nullable
as String?,il: freezed == il ? _self.il : il // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$Relazioni {

 bool get completo; List<String> get mancanti;
/// Create a copy of Relazioni
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RelazioniCopyWith<Relazioni> get copyWith => _$RelazioniCopyWithImpl<Relazioni>(this as Relazioni, _$identity);

  /// Serializes this Relazioni to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Relazioni;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Relazioni&&(identical(other.completo, _this.completo) || other.completo == _this.completo)&&const DeepCollectionEquality().equals(other.mancanti, _this.mancanti));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Relazioni;
  return Object.hash(runtimeType,_this.completo,const DeepCollectionEquality().hash(_this.mancanti));
}

@override
String toString() {
  final _this = this as Relazioni;
  return 'Relazioni(completo: ${_this.completo}, mancanti: ${_this.mancanti})';
}


}

/// @nodoc
abstract mixin class $RelazioniCopyWith<$Res>  {
  factory $RelazioniCopyWith(Relazioni value, $Res Function(Relazioni) _then) = _$RelazioniCopyWithImpl;
@useResult
$Res call({
 bool completo, List<String> mancanti
});




}
/// @nodoc
class _$RelazioniCopyWithImpl<$Res>
    implements $RelazioniCopyWith<$Res> {
  _$RelazioniCopyWithImpl(this._self, this._then);

  final Relazioni _self;
  final $Res Function(Relazioni) _then;

/// Create a copy of Relazioni
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? completo = null,Object? mancanti = null,}) {
  return _then(Relazioni(
completo: null == completo ? _self.completo : completo // ignore: cast_nullable_to_non_nullable
as bool,mancanti: null == mancanti ? _self.mancanti : mancanti // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}

}


/// Adds pattern-matching-related methods to [Relazioni].
extension RelazioniPatterns on Relazioni {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Relazioni value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Relazioni() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Relazioni value)  $default,){
final _that = this;
switch (_that) {
case _Relazioni():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Relazioni value)?  $default,){
final _that = this;
switch (_that) {
case _Relazioni() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( bool completo,  List<String> mancanti)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Relazioni() when $default != null:
return $default(_that.completo,_that.mancanti);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( bool completo,  List<String> mancanti)  $default,) {final _that = this;
switch (_that) {
case _Relazioni():
return $default(_that.completo,_that.mancanti);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( bool completo,  List<String> mancanti)?  $default,) {final _that = this;
switch (_that) {
case _Relazioni() when $default != null:
return $default(_that.completo,_that.mancanti);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Relazioni implements Relazioni {
  const _Relazioni({this.completo = true,  List<String> mancanti = const <String>[]}): _mancanti = mancanti;
  factory _Relazioni.fromJson(Map<String, dynamic> json) => _$RelazioniFromJson(json);

@override@JsonKey() final  bool completo;
 final  List<String> _mancanti;
@override@JsonKey() List<String> get mancanti {
  if (_mancanti is EqualUnmodifiableListView) return _mancanti;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_mancanti);
}


/// Create a copy of Relazioni
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RelazioniCopyWith<_Relazioni> get copyWith => __$RelazioniCopyWithImpl<_Relazioni>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$RelazioniToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Relazioni&&(identical(other.completo, completo) || other.completo == completo)&&const DeepCollectionEquality().equals(other.mancanti, _mancanti));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,completo,const DeepCollectionEquality().hash(_mancanti));
}

@override
String toString() {
    return 'Relazioni(completo: $completo, mancanti: $mancanti)';
}


}

/// @nodoc
abstract mixin class _$RelazioniCopyWith<$Res> implements $RelazioniCopyWith<$Res> {
  factory _$RelazioniCopyWith(_Relazioni value, $Res Function(_Relazioni) _then) = __$RelazioniCopyWithImpl;
@override @useResult
$Res call({
 bool completo, List<String> mancanti
});




}
/// @nodoc
class __$RelazioniCopyWithImpl<$Res>
    implements _$RelazioniCopyWith<$Res> {
  __$RelazioniCopyWithImpl(this._self, this._then);

  final _Relazioni _self;
  final $Res Function(_Relazioni) _then;

/// Create a copy of Relazioni
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? completo = null,Object? mancanti = null,}) {
  return _then(_Relazioni(
completo: null == completo ? _self.completo : completo // ignore: cast_nullable_to_non_nullable
as bool,mancanti: null == mancanti ? _self._mancanti : mancanti // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}


}


/// @nodoc
mixin _$OrigineDato {

 String get da; String get il;
/// Create a copy of OrigineDato
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$OrigineDatoCopyWith<OrigineDato> get copyWith => _$OrigineDatoCopyWithImpl<OrigineDato>(this as OrigineDato, _$identity);

  /// Serializes this OrigineDato to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as OrigineDato;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is OrigineDato&&(identical(other.da, _this.da) || other.da == _this.da)&&(identical(other.il, _this.il) || other.il == _this.il));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as OrigineDato;
  return Object.hash(runtimeType,_this.da,_this.il);
}

@override
String toString() {
  final _this = this as OrigineDato;
  return 'OrigineDato(da: ${_this.da}, il: ${_this.il})';
}


}

/// @nodoc
abstract mixin class $OrigineDatoCopyWith<$Res>  {
  factory $OrigineDatoCopyWith(OrigineDato value, $Res Function(OrigineDato) _then) = _$OrigineDatoCopyWithImpl;
@useResult
$Res call({
 String da, String il
});




}
/// @nodoc
class _$OrigineDatoCopyWithImpl<$Res>
    implements $OrigineDatoCopyWith<$Res> {
  _$OrigineDatoCopyWithImpl(this._self, this._then);

  final OrigineDato _self;
  final $Res Function(OrigineDato) _then;

/// Create a copy of OrigineDato
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? da = null,Object? il = null,}) {
  return _then(OrigineDato(
da: null == da ? _self.da : da // ignore: cast_nullable_to_non_nullable
as String,il: null == il ? _self.il : il // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [OrigineDato].
extension OrigineDatoPatterns on OrigineDato {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _OrigineDato value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _OrigineDato() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _OrigineDato value)  $default,){
final _that = this;
switch (_that) {
case _OrigineDato():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _OrigineDato value)?  $default,){
final _that = this;
switch (_that) {
case _OrigineDato() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String da,  String il)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _OrigineDato() when $default != null:
return $default(_that.da,_that.il);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String da,  String il)  $default,) {final _that = this;
switch (_that) {
case _OrigineDato():
return $default(_that.da,_that.il);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String da,  String il)?  $default,) {final _that = this;
switch (_that) {
case _OrigineDato() when $default != null:
return $default(_that.da,_that.il);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _OrigineDato implements OrigineDato {
  const _OrigineDato({required this.da, required this.il});
  factory _OrigineDato.fromJson(Map<String, dynamic> json) => _$OrigineDatoFromJson(json);

@override final  String da;
@override final  String il;

/// Create a copy of OrigineDato
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$OrigineDatoCopyWith<_OrigineDato> get copyWith => __$OrigineDatoCopyWithImpl<_OrigineDato>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$OrigineDatoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _OrigineDato&&(identical(other.da, da) || other.da == da)&&(identical(other.il, il) || other.il == il));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,da,il);
}

@override
String toString() {
    return 'OrigineDato(da: $da, il: $il)';
}


}

/// @nodoc
abstract mixin class _$OrigineDatoCopyWith<$Res> implements $OrigineDatoCopyWith<$Res> {
  factory _$OrigineDatoCopyWith(_OrigineDato value, $Res Function(_OrigineDato) _then) = __$OrigineDatoCopyWithImpl;
@override @useResult
$Res call({
 String da, String il
});




}
/// @nodoc
class __$OrigineDatoCopyWithImpl<$Res>
    implements _$OrigineDatoCopyWith<$Res> {
  __$OrigineDatoCopyWithImpl(this._self, this._then);

  final _OrigineDato _self;
  final $Res Function(_OrigineDato) _then;

/// Create a copy of OrigineDato
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? da = null,Object? il = null,}) {
  return _then(_OrigineDato(
da: null == da ? _self.da : da // ignore: cast_nullable_to_non_nullable
as String,il: null == il ? _self.il : il // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$Profilo {

 int get id; String? get email; String? get displayName; String get locale;/// v9.5: la versione della lettura di questa persona (`chat` o `classica`), fissata alla sua prima lettura e
/// uguale su tutti i dispositivi; `null` = ancora nessuna.
 String? get varianteLettura;/// Fase 2d: quando la lingua è stata scelta dal sito o dall'app; `null` = mai.
 String? get localeSceltaIl; String? get birthDate;/// `donna`, `uomo`, `non_binario`, `altro`, `non_dice`.
 String? get gender; String? get genderCustom; bool get isTrans;@JsonKey(name: 'promemoria_2fa') bool get promemoria2fa; String? get nomePubblico;/// `esoterico` o `quotidiano`.
 String get registroLinguistico; int? get mazzoPredefinitoId; String get nomeMostrato;/// Percorso relativo dell'API.
 String? get avatar; PersonaSalvata? get partnerRicordato; Relazioni get relazioni; String? get referralCode; bool get invitato; Condivisioni get condivisioni; Carta? get cartaAnima; Carta? get cartaAnno; String? get nome; String? get cognome; PosizioneAttuale? get posizione; Map<String, OrigineDato> get datiSocial; bool? get importaSocial; bool? get rilevaPosizione;
/// Create a copy of Profilo
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProfiloCopyWith<Profilo> get copyWith => _$ProfiloCopyWithImpl<Profilo>(this as Profilo, _$identity);

  /// Serializes this Profilo to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Profilo;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Profilo&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.email, _this.email) || other.email == _this.email)&&(identical(other.displayName, _this.displayName) || other.displayName == _this.displayName)&&(identical(other.locale, _this.locale) || other.locale == _this.locale)&&(identical(other.varianteLettura, _this.varianteLettura) || other.varianteLettura == _this.varianteLettura)&&(identical(other.localeSceltaIl, _this.localeSceltaIl) || other.localeSceltaIl == _this.localeSceltaIl)&&(identical(other.birthDate, _this.birthDate) || other.birthDate == _this.birthDate)&&(identical(other.gender, _this.gender) || other.gender == _this.gender)&&(identical(other.genderCustom, _this.genderCustom) || other.genderCustom == _this.genderCustom)&&(identical(other.isTrans, _this.isTrans) || other.isTrans == _this.isTrans)&&(identical(other.promemoria2fa, _this.promemoria2fa) || other.promemoria2fa == _this.promemoria2fa)&&(identical(other.nomePubblico, _this.nomePubblico) || other.nomePubblico == _this.nomePubblico)&&(identical(other.registroLinguistico, _this.registroLinguistico) || other.registroLinguistico == _this.registroLinguistico)&&(identical(other.mazzoPredefinitoId, _this.mazzoPredefinitoId) || other.mazzoPredefinitoId == _this.mazzoPredefinitoId)&&(identical(other.nomeMostrato, _this.nomeMostrato) || other.nomeMostrato == _this.nomeMostrato)&&(identical(other.avatar, _this.avatar) || other.avatar == _this.avatar)&&(identical(other.partnerRicordato, _this.partnerRicordato) || other.partnerRicordato == _this.partnerRicordato)&&(identical(other.relazioni, _this.relazioni) || other.relazioni == _this.relazioni)&&(identical(other.referralCode, _this.referralCode) || other.referralCode == _this.referralCode)&&(identical(other.invitato, _this.invitato) || other.invitato == _this.invitato)&&(identical(other.condivisioni, _this.condivisioni) || other.condivisioni == _this.condivisioni)&&(identical(other.cartaAnima, _this.cartaAnima) || other.cartaAnima == _this.cartaAnima)&&(identical(other.cartaAnno, _this.cartaAnno) || other.cartaAnno == _this.cartaAnno)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.cognome, _this.cognome) || other.cognome == _this.cognome)&&(identical(other.posizione, _this.posizione) || other.posizione == _this.posizione)&&const DeepCollectionEquality().equals(other.datiSocial, _this.datiSocial)&&(identical(other.importaSocial, _this.importaSocial) || other.importaSocial == _this.importaSocial)&&(identical(other.rilevaPosizione, _this.rilevaPosizione) || other.rilevaPosizione == _this.rilevaPosizione));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Profilo;
  return Object.hashAll([runtimeType,_this.id,_this.email,_this.displayName,_this.locale,_this.varianteLettura,_this.localeSceltaIl,_this.birthDate,_this.gender,_this.genderCustom,_this.isTrans,_this.promemoria2fa,_this.nomePubblico,_this.registroLinguistico,_this.mazzoPredefinitoId,_this.nomeMostrato,_this.avatar,_this.partnerRicordato,_this.relazioni,_this.referralCode,_this.invitato,_this.condivisioni,_this.cartaAnima,_this.cartaAnno,_this.nome,_this.cognome,_this.posizione,const DeepCollectionEquality().hash(_this.datiSocial),_this.importaSocial,_this.rilevaPosizione]);
}

@override
String toString() {
  final _this = this as Profilo;
  return 'Profilo(id: ${_this.id}, email: ${_this.email}, displayName: ${_this.displayName}, locale: ${_this.locale}, varianteLettura: ${_this.varianteLettura}, localeSceltaIl: ${_this.localeSceltaIl}, birthDate: ${_this.birthDate}, gender: ${_this.gender}, genderCustom: ${_this.genderCustom}, isTrans: ${_this.isTrans}, promemoria2fa: ${_this.promemoria2fa}, nomePubblico: ${_this.nomePubblico}, registroLinguistico: ${_this.registroLinguistico}, mazzoPredefinitoId: ${_this.mazzoPredefinitoId}, nomeMostrato: ${_this.nomeMostrato}, avatar: ${_this.avatar}, partnerRicordato: ${_this.partnerRicordato}, relazioni: ${_this.relazioni}, referralCode: ${_this.referralCode}, invitato: ${_this.invitato}, condivisioni: ${_this.condivisioni}, cartaAnima: ${_this.cartaAnima}, cartaAnno: ${_this.cartaAnno}, nome: ${_this.nome}, cognome: ${_this.cognome}, posizione: ${_this.posizione}, datiSocial: ${_this.datiSocial}, importaSocial: ${_this.importaSocial}, rilevaPosizione: ${_this.rilevaPosizione})';
}


}

/// @nodoc
abstract mixin class $ProfiloCopyWith<$Res>  {
  factory $ProfiloCopyWith(Profilo value, $Res Function(Profilo) _then) = _$ProfiloCopyWithImpl;
@useResult
$Res call({
 int id, String? email, String? displayName, String locale, String? varianteLettura, String? localeSceltaIl, String? birthDate, String? gender, String? genderCustom, bool isTrans,@JsonKey(name: 'promemoria_2fa') bool promemoria2fa, String? nomePubblico, String registroLinguistico, int? mazzoPredefinitoId, String nomeMostrato, String? avatar, PersonaSalvata? partnerRicordato, Relazioni relazioni, String? referralCode, bool invitato, Condivisioni condivisioni, Carta? cartaAnima, Carta? cartaAnno, String? nome, String? cognome, PosizioneAttuale? posizione, Map<String, OrigineDato> datiSocial, bool? importaSocial, bool? rilevaPosizione
});


$PersonaSalvataCopyWith<$Res>? get partnerRicordato;$RelazioniCopyWith<$Res> get relazioni;$CondivisioniCopyWith<$Res> get condivisioni;$CartaCopyWith<$Res>? get cartaAnima;$CartaCopyWith<$Res>? get cartaAnno;$PosizioneAttualeCopyWith<$Res>? get posizione;

}
/// @nodoc
class _$ProfiloCopyWithImpl<$Res>
    implements $ProfiloCopyWith<$Res> {
  _$ProfiloCopyWithImpl(this._self, this._then);

  final Profilo _self;
  final $Res Function(Profilo) _then;

/// Create a copy of Profilo
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? email = freezed,Object? displayName = freezed,Object? locale = null,Object? varianteLettura = freezed,Object? localeSceltaIl = freezed,Object? birthDate = freezed,Object? gender = freezed,Object? genderCustom = freezed,Object? isTrans = null,Object? promemoria2fa = null,Object? nomePubblico = freezed,Object? registroLinguistico = null,Object? mazzoPredefinitoId = freezed,Object? nomeMostrato = null,Object? avatar = freezed,Object? partnerRicordato = freezed,Object? relazioni = null,Object? referralCode = freezed,Object? invitato = null,Object? condivisioni = null,Object? cartaAnima = freezed,Object? cartaAnno = freezed,Object? nome = freezed,Object? cognome = freezed,Object? posizione = freezed,Object? datiSocial = null,Object? importaSocial = freezed,Object? rilevaPosizione = freezed,}) {
  return _then(Profilo(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,email: freezed == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String?,displayName: freezed == displayName ? _self.displayName : displayName // ignore: cast_nullable_to_non_nullable
as String?,locale: null == locale ? _self.locale : locale // ignore: cast_nullable_to_non_nullable
as String,varianteLettura: freezed == varianteLettura ? _self.varianteLettura : varianteLettura // ignore: cast_nullable_to_non_nullable
as String?,localeSceltaIl: freezed == localeSceltaIl ? _self.localeSceltaIl : localeSceltaIl // ignore: cast_nullable_to_non_nullable
as String?,birthDate: freezed == birthDate ? _self.birthDate : birthDate // ignore: cast_nullable_to_non_nullable
as String?,gender: freezed == gender ? _self.gender : gender // ignore: cast_nullable_to_non_nullable
as String?,genderCustom: freezed == genderCustom ? _self.genderCustom : genderCustom // ignore: cast_nullable_to_non_nullable
as String?,isTrans: null == isTrans ? _self.isTrans : isTrans // ignore: cast_nullable_to_non_nullable
as bool,promemoria2fa: null == promemoria2fa ? _self.promemoria2fa : promemoria2fa // ignore: cast_nullable_to_non_nullable
as bool,nomePubblico: freezed == nomePubblico ? _self.nomePubblico : nomePubblico // ignore: cast_nullable_to_non_nullable
as String?,registroLinguistico: null == registroLinguistico ? _self.registroLinguistico : registroLinguistico // ignore: cast_nullable_to_non_nullable
as String,mazzoPredefinitoId: freezed == mazzoPredefinitoId ? _self.mazzoPredefinitoId : mazzoPredefinitoId // ignore: cast_nullable_to_non_nullable
as int?,nomeMostrato: null == nomeMostrato ? _self.nomeMostrato : nomeMostrato // ignore: cast_nullable_to_non_nullable
as String,avatar: freezed == avatar ? _self.avatar : avatar // ignore: cast_nullable_to_non_nullable
as String?,partnerRicordato: freezed == partnerRicordato ? _self.partnerRicordato : partnerRicordato // ignore: cast_nullable_to_non_nullable
as PersonaSalvata?,relazioni: null == relazioni ? _self.relazioni : relazioni // ignore: cast_nullable_to_non_nullable
as Relazioni,referralCode: freezed == referralCode ? _self.referralCode : referralCode // ignore: cast_nullable_to_non_nullable
as String?,invitato: null == invitato ? _self.invitato : invitato // ignore: cast_nullable_to_non_nullable
as bool,condivisioni: null == condivisioni ? _self.condivisioni : condivisioni // ignore: cast_nullable_to_non_nullable
as Condivisioni,cartaAnima: freezed == cartaAnima ? _self.cartaAnima : cartaAnima // ignore: cast_nullable_to_non_nullable
as Carta?,cartaAnno: freezed == cartaAnno ? _self.cartaAnno : cartaAnno // ignore: cast_nullable_to_non_nullable
as Carta?,nome: freezed == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String?,cognome: freezed == cognome ? _self.cognome : cognome // ignore: cast_nullable_to_non_nullable
as String?,posizione: freezed == posizione ? _self.posizione : posizione // ignore: cast_nullable_to_non_nullable
as PosizioneAttuale?,datiSocial: null == datiSocial ? _self.datiSocial : datiSocial // ignore: cast_nullable_to_non_nullable
as Map<String, OrigineDato>,importaSocial: freezed == importaSocial ? _self.importaSocial : importaSocial // ignore: cast_nullable_to_non_nullable
as bool?,rilevaPosizione: freezed == rilevaPosizione ? _self.rilevaPosizione : rilevaPosizione // ignore: cast_nullable_to_non_nullable
as bool?,
  ));
}
/// Create a copy of Profilo
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PersonaSalvataCopyWith<$Res>? get partnerRicordato {
    if (_self.partnerRicordato == null) {
    return null;
  }

  return $PersonaSalvataCopyWith<$Res>(_self.partnerRicordato!, (value) {
    return _then(_self.copyWith(partnerRicordato: value));
  });
}/// Create a copy of Profilo
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$RelazioniCopyWith<$Res> get relazioni {
  
  return $RelazioniCopyWith<$Res>(_self.relazioni, (value) {
    return _then(_self.copyWith(relazioni: value));
  });
}/// Create a copy of Profilo
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CondivisioniCopyWith<$Res> get condivisioni {
  
  return $CondivisioniCopyWith<$Res>(_self.condivisioni, (value) {
    return _then(_self.copyWith(condivisioni: value));
  });
}/// Create a copy of Profilo
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CartaCopyWith<$Res>? get cartaAnima {
    if (_self.cartaAnima == null) {
    return null;
  }

  return $CartaCopyWith<$Res>(_self.cartaAnima!, (value) {
    return _then(_self.copyWith(cartaAnima: value));
  });
}/// Create a copy of Profilo
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CartaCopyWith<$Res>? get cartaAnno {
    if (_self.cartaAnno == null) {
    return null;
  }

  return $CartaCopyWith<$Res>(_self.cartaAnno!, (value) {
    return _then(_self.copyWith(cartaAnno: value));
  });
}/// Create a copy of Profilo
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PosizioneAttualeCopyWith<$Res>? get posizione {
    if (_self.posizione == null) {
    return null;
  }

  return $PosizioneAttualeCopyWith<$Res>(_self.posizione!, (value) {
    return _then(_self.copyWith(posizione: value));
  });
}
}


/// Adds pattern-matching-related methods to [Profilo].
extension ProfiloPatterns on Profilo {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Profilo value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Profilo() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Profilo value)  $default,){
final _that = this;
switch (_that) {
case _Profilo():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Profilo value)?  $default,){
final _that = this;
switch (_that) {
case _Profilo() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String? email,  String? displayName,  String locale,  String? varianteLettura,  String? localeSceltaIl,  String? birthDate,  String? gender,  String? genderCustom,  bool isTrans, @JsonKey(name: 'promemoria_2fa')  bool promemoria2fa,  String? nomePubblico,  String registroLinguistico,  int? mazzoPredefinitoId,  String nomeMostrato,  String? avatar,  PersonaSalvata? partnerRicordato,  Relazioni relazioni,  String? referralCode,  bool invitato,  Condivisioni condivisioni,  Carta? cartaAnima,  Carta? cartaAnno,  String? nome,  String? cognome,  PosizioneAttuale? posizione,  Map<String, OrigineDato> datiSocial,  bool? importaSocial,  bool? rilevaPosizione)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Profilo() when $default != null:
return $default(_that.id,_that.email,_that.displayName,_that.locale,_that.varianteLettura,_that.localeSceltaIl,_that.birthDate,_that.gender,_that.genderCustom,_that.isTrans,_that.promemoria2fa,_that.nomePubblico,_that.registroLinguistico,_that.mazzoPredefinitoId,_that.nomeMostrato,_that.avatar,_that.partnerRicordato,_that.relazioni,_that.referralCode,_that.invitato,_that.condivisioni,_that.cartaAnima,_that.cartaAnno,_that.nome,_that.cognome,_that.posizione,_that.datiSocial,_that.importaSocial,_that.rilevaPosizione);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String? email,  String? displayName,  String locale,  String? varianteLettura,  String? localeSceltaIl,  String? birthDate,  String? gender,  String? genderCustom,  bool isTrans, @JsonKey(name: 'promemoria_2fa')  bool promemoria2fa,  String? nomePubblico,  String registroLinguistico,  int? mazzoPredefinitoId,  String nomeMostrato,  String? avatar,  PersonaSalvata? partnerRicordato,  Relazioni relazioni,  String? referralCode,  bool invitato,  Condivisioni condivisioni,  Carta? cartaAnima,  Carta? cartaAnno,  String? nome,  String? cognome,  PosizioneAttuale? posizione,  Map<String, OrigineDato> datiSocial,  bool? importaSocial,  bool? rilevaPosizione)  $default,) {final _that = this;
switch (_that) {
case _Profilo():
return $default(_that.id,_that.email,_that.displayName,_that.locale,_that.varianteLettura,_that.localeSceltaIl,_that.birthDate,_that.gender,_that.genderCustom,_that.isTrans,_that.promemoria2fa,_that.nomePubblico,_that.registroLinguistico,_that.mazzoPredefinitoId,_that.nomeMostrato,_that.avatar,_that.partnerRicordato,_that.relazioni,_that.referralCode,_that.invitato,_that.condivisioni,_that.cartaAnima,_that.cartaAnno,_that.nome,_that.cognome,_that.posizione,_that.datiSocial,_that.importaSocial,_that.rilevaPosizione);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String? email,  String? displayName,  String locale,  String? varianteLettura,  String? localeSceltaIl,  String? birthDate,  String? gender,  String? genderCustom,  bool isTrans, @JsonKey(name: 'promemoria_2fa')  bool promemoria2fa,  String? nomePubblico,  String registroLinguistico,  int? mazzoPredefinitoId,  String nomeMostrato,  String? avatar,  PersonaSalvata? partnerRicordato,  Relazioni relazioni,  String? referralCode,  bool invitato,  Condivisioni condivisioni,  Carta? cartaAnima,  Carta? cartaAnno,  String? nome,  String? cognome,  PosizioneAttuale? posizione,  Map<String, OrigineDato> datiSocial,  bool? importaSocial,  bool? rilevaPosizione)?  $default,) {final _that = this;
switch (_that) {
case _Profilo() when $default != null:
return $default(_that.id,_that.email,_that.displayName,_that.locale,_that.varianteLettura,_that.localeSceltaIl,_that.birthDate,_that.gender,_that.genderCustom,_that.isTrans,_that.promemoria2fa,_that.nomePubblico,_that.registroLinguistico,_that.mazzoPredefinitoId,_that.nomeMostrato,_that.avatar,_that.partnerRicordato,_that.relazioni,_that.referralCode,_that.invitato,_that.condivisioni,_that.cartaAnima,_that.cartaAnno,_that.nome,_that.cognome,_that.posizione,_that.datiSocial,_that.importaSocial,_that.rilevaPosizione);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Profilo implements Profilo {
  const _Profilo({required this.id, this.email, this.displayName, this.locale = 'it', this.varianteLettura, this.localeSceltaIl, this.birthDate, this.gender, this.genderCustom, this.isTrans = false, @JsonKey(name: 'promemoria_2fa') this.promemoria2fa = true, this.nomePubblico, this.registroLinguistico = 'esoterico', this.mazzoPredefinitoId, this.nomeMostrato = '', this.avatar, this.partnerRicordato, this.relazioni = const Relazioni(), this.referralCode, this.invitato = false, this.condivisioni = const Condivisioni(), this.cartaAnima, this.cartaAnno, this.nome, this.cognome, this.posizione,  Map<String, OrigineDato> datiSocial = const <String, OrigineDato>{}, this.importaSocial, this.rilevaPosizione}): _datiSocial = datiSocial;
  factory _Profilo.fromJson(Map<String, dynamic> json) => _$ProfiloFromJson(json);

@override final  int id;
@override final  String? email;
@override final  String? displayName;
@override@JsonKey() final  String locale;
/// v9.5: la versione della lettura di questa persona (`chat` o `classica`), fissata alla sua prima lettura e
/// uguale su tutti i dispositivi; `null` = ancora nessuna.
@override final  String? varianteLettura;
/// Fase 2d: quando la lingua è stata scelta dal sito o dall'app; `null` = mai.
@override final  String? localeSceltaIl;
@override final  String? birthDate;
/// `donna`, `uomo`, `non_binario`, `altro`, `non_dice`.
@override final  String? gender;
@override final  String? genderCustom;
@override@JsonKey() final  bool isTrans;
@override@JsonKey(name: 'promemoria_2fa') final  bool promemoria2fa;
@override final  String? nomePubblico;
/// `esoterico` o `quotidiano`.
@override@JsonKey() final  String registroLinguistico;
@override final  int? mazzoPredefinitoId;
@override@JsonKey() final  String nomeMostrato;
/// Percorso relativo dell'API.
@override final  String? avatar;
@override final  PersonaSalvata? partnerRicordato;
@override@JsonKey() final  Relazioni relazioni;
@override final  String? referralCode;
@override@JsonKey() final  bool invitato;
@override@JsonKey() final  Condivisioni condivisioni;
@override final  Carta? cartaAnima;
@override final  Carta? cartaAnno;
@override final  String? nome;
@override final  String? cognome;
@override final  PosizioneAttuale? posizione;
 final  Map<String, OrigineDato> _datiSocial;
@override@JsonKey() Map<String, OrigineDato> get datiSocial {
  if (_datiSocial is EqualUnmodifiableMapView) return _datiSocial;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_datiSocial);
}

@override final  bool? importaSocial;
@override final  bool? rilevaPosizione;

/// Create a copy of Profilo
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ProfiloCopyWith<_Profilo> get copyWith => __$ProfiloCopyWithImpl<_Profilo>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ProfiloToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Profilo&&(identical(other.id, id) || other.id == id)&&(identical(other.email, email) || other.email == email)&&(identical(other.displayName, displayName) || other.displayName == displayName)&&(identical(other.locale, locale) || other.locale == locale)&&(identical(other.varianteLettura, varianteLettura) || other.varianteLettura == varianteLettura)&&(identical(other.localeSceltaIl, localeSceltaIl) || other.localeSceltaIl == localeSceltaIl)&&(identical(other.birthDate, birthDate) || other.birthDate == birthDate)&&(identical(other.gender, gender) || other.gender == gender)&&(identical(other.genderCustom, genderCustom) || other.genderCustom == genderCustom)&&(identical(other.isTrans, isTrans) || other.isTrans == isTrans)&&(identical(other.promemoria2fa, promemoria2fa) || other.promemoria2fa == promemoria2fa)&&(identical(other.nomePubblico, nomePubblico) || other.nomePubblico == nomePubblico)&&(identical(other.registroLinguistico, registroLinguistico) || other.registroLinguistico == registroLinguistico)&&(identical(other.mazzoPredefinitoId, mazzoPredefinitoId) || other.mazzoPredefinitoId == mazzoPredefinitoId)&&(identical(other.nomeMostrato, nomeMostrato) || other.nomeMostrato == nomeMostrato)&&(identical(other.avatar, avatar) || other.avatar == avatar)&&(identical(other.partnerRicordato, partnerRicordato) || other.partnerRicordato == partnerRicordato)&&(identical(other.relazioni, relazioni) || other.relazioni == relazioni)&&(identical(other.referralCode, referralCode) || other.referralCode == referralCode)&&(identical(other.invitato, invitato) || other.invitato == invitato)&&(identical(other.condivisioni, condivisioni) || other.condivisioni == condivisioni)&&(identical(other.cartaAnima, cartaAnima) || other.cartaAnima == cartaAnima)&&(identical(other.cartaAnno, cartaAnno) || other.cartaAnno == cartaAnno)&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.cognome, cognome) || other.cognome == cognome)&&(identical(other.posizione, posizione) || other.posizione == posizione)&&const DeepCollectionEquality().equals(other.datiSocial, _datiSocial)&&(identical(other.importaSocial, importaSocial) || other.importaSocial == importaSocial)&&(identical(other.rilevaPosizione, rilevaPosizione) || other.rilevaPosizione == rilevaPosizione));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hashAll([runtimeType,id,email,displayName,locale,varianteLettura,localeSceltaIl,birthDate,gender,genderCustom,isTrans,promemoria2fa,nomePubblico,registroLinguistico,mazzoPredefinitoId,nomeMostrato,avatar,partnerRicordato,relazioni,referralCode,invitato,condivisioni,cartaAnima,cartaAnno,nome,cognome,posizione,const DeepCollectionEquality().hash(_datiSocial),importaSocial,rilevaPosizione]);
}

@override
String toString() {
    return 'Profilo(id: $id, email: $email, displayName: $displayName, locale: $locale, varianteLettura: $varianteLettura, localeSceltaIl: $localeSceltaIl, birthDate: $birthDate, gender: $gender, genderCustom: $genderCustom, isTrans: $isTrans, promemoria2fa: $promemoria2fa, nomePubblico: $nomePubblico, registroLinguistico: $registroLinguistico, mazzoPredefinitoId: $mazzoPredefinitoId, nomeMostrato: $nomeMostrato, avatar: $avatar, partnerRicordato: $partnerRicordato, relazioni: $relazioni, referralCode: $referralCode, invitato: $invitato, condivisioni: $condivisioni, cartaAnima: $cartaAnima, cartaAnno: $cartaAnno, nome: $nome, cognome: $cognome, posizione: $posizione, datiSocial: $datiSocial, importaSocial: $importaSocial, rilevaPosizione: $rilevaPosizione)';
}


}

/// @nodoc
abstract mixin class _$ProfiloCopyWith<$Res> implements $ProfiloCopyWith<$Res> {
  factory _$ProfiloCopyWith(_Profilo value, $Res Function(_Profilo) _then) = __$ProfiloCopyWithImpl;
@override @useResult
$Res call({
 int id, String? email, String? displayName, String locale, String? varianteLettura, String? localeSceltaIl, String? birthDate, String? gender, String? genderCustom, bool isTrans,@JsonKey(name: 'promemoria_2fa') bool promemoria2fa, String? nomePubblico, String registroLinguistico, int? mazzoPredefinitoId, String nomeMostrato, String? avatar, PersonaSalvata? partnerRicordato, Relazioni relazioni, String? referralCode, bool invitato, Condivisioni condivisioni, Carta? cartaAnima, Carta? cartaAnno, String? nome, String? cognome, PosizioneAttuale? posizione, Map<String, OrigineDato> datiSocial, bool? importaSocial, bool? rilevaPosizione
});


@override $PersonaSalvataCopyWith<$Res>? get partnerRicordato;@override $RelazioniCopyWith<$Res> get relazioni;@override $CondivisioniCopyWith<$Res> get condivisioni;@override $CartaCopyWith<$Res>? get cartaAnima;@override $CartaCopyWith<$Res>? get cartaAnno;@override $PosizioneAttualeCopyWith<$Res>? get posizione;

}
/// @nodoc
class __$ProfiloCopyWithImpl<$Res>
    implements _$ProfiloCopyWith<$Res> {
  __$ProfiloCopyWithImpl(this._self, this._then);

  final _Profilo _self;
  final $Res Function(_Profilo) _then;

/// Create a copy of Profilo
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? email = freezed,Object? displayName = freezed,Object? locale = null,Object? varianteLettura = freezed,Object? localeSceltaIl = freezed,Object? birthDate = freezed,Object? gender = freezed,Object? genderCustom = freezed,Object? isTrans = null,Object? promemoria2fa = null,Object? nomePubblico = freezed,Object? registroLinguistico = null,Object? mazzoPredefinitoId = freezed,Object? nomeMostrato = null,Object? avatar = freezed,Object? partnerRicordato = freezed,Object? relazioni = null,Object? referralCode = freezed,Object? invitato = null,Object? condivisioni = null,Object? cartaAnima = freezed,Object? cartaAnno = freezed,Object? nome = freezed,Object? cognome = freezed,Object? posizione = freezed,Object? datiSocial = null,Object? importaSocial = freezed,Object? rilevaPosizione = freezed,}) {
  return _then(_Profilo(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,email: freezed == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String?,displayName: freezed == displayName ? _self.displayName : displayName // ignore: cast_nullable_to_non_nullable
as String?,locale: null == locale ? _self.locale : locale // ignore: cast_nullable_to_non_nullable
as String,varianteLettura: freezed == varianteLettura ? _self.varianteLettura : varianteLettura // ignore: cast_nullable_to_non_nullable
as String?,localeSceltaIl: freezed == localeSceltaIl ? _self.localeSceltaIl : localeSceltaIl // ignore: cast_nullable_to_non_nullable
as String?,birthDate: freezed == birthDate ? _self.birthDate : birthDate // ignore: cast_nullable_to_non_nullable
as String?,gender: freezed == gender ? _self.gender : gender // ignore: cast_nullable_to_non_nullable
as String?,genderCustom: freezed == genderCustom ? _self.genderCustom : genderCustom // ignore: cast_nullable_to_non_nullable
as String?,isTrans: null == isTrans ? _self.isTrans : isTrans // ignore: cast_nullable_to_non_nullable
as bool,promemoria2fa: null == promemoria2fa ? _self.promemoria2fa : promemoria2fa // ignore: cast_nullable_to_non_nullable
as bool,nomePubblico: freezed == nomePubblico ? _self.nomePubblico : nomePubblico // ignore: cast_nullable_to_non_nullable
as String?,registroLinguistico: null == registroLinguistico ? _self.registroLinguistico : registroLinguistico // ignore: cast_nullable_to_non_nullable
as String,mazzoPredefinitoId: freezed == mazzoPredefinitoId ? _self.mazzoPredefinitoId : mazzoPredefinitoId // ignore: cast_nullable_to_non_nullable
as int?,nomeMostrato: null == nomeMostrato ? _self.nomeMostrato : nomeMostrato // ignore: cast_nullable_to_non_nullable
as String,avatar: freezed == avatar ? _self.avatar : avatar // ignore: cast_nullable_to_non_nullable
as String?,partnerRicordato: freezed == partnerRicordato ? _self.partnerRicordato : partnerRicordato // ignore: cast_nullable_to_non_nullable
as PersonaSalvata?,relazioni: null == relazioni ? _self.relazioni : relazioni // ignore: cast_nullable_to_non_nullable
as Relazioni,referralCode: freezed == referralCode ? _self.referralCode : referralCode // ignore: cast_nullable_to_non_nullable
as String?,invitato: null == invitato ? _self.invitato : invitato // ignore: cast_nullable_to_non_nullable
as bool,condivisioni: null == condivisioni ? _self.condivisioni : condivisioni // ignore: cast_nullable_to_non_nullable
as Condivisioni,cartaAnima: freezed == cartaAnima ? _self.cartaAnima : cartaAnima // ignore: cast_nullable_to_non_nullable
as Carta?,cartaAnno: freezed == cartaAnno ? _self.cartaAnno : cartaAnno // ignore: cast_nullable_to_non_nullable
as Carta?,nome: freezed == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String?,cognome: freezed == cognome ? _self.cognome : cognome // ignore: cast_nullable_to_non_nullable
as String?,posizione: freezed == posizione ? _self.posizione : posizione // ignore: cast_nullable_to_non_nullable
as PosizioneAttuale?,datiSocial: null == datiSocial ? _self._datiSocial : datiSocial // ignore: cast_nullable_to_non_nullable
as Map<String, OrigineDato>,importaSocial: freezed == importaSocial ? _self.importaSocial : importaSocial // ignore: cast_nullable_to_non_nullable
as bool?,rilevaPosizione: freezed == rilevaPosizione ? _self.rilevaPosizione : rilevaPosizione // ignore: cast_nullable_to_non_nullable
as bool?,
  ));
}

/// Create a copy of Profilo
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PersonaSalvataCopyWith<$Res>? get partnerRicordato {
    if (_self.partnerRicordato == null) {
    return null;
  }

  return $PersonaSalvataCopyWith<$Res>(_self.partnerRicordato!, (value) {
    return _then(_self.copyWith(partnerRicordato: value));
  });
}/// Create a copy of Profilo
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$RelazioniCopyWith<$Res> get relazioni {
  
  return $RelazioniCopyWith<$Res>(_self.relazioni, (value) {
    return _then(_self.copyWith(relazioni: value));
  });
}/// Create a copy of Profilo
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CondivisioniCopyWith<$Res> get condivisioni {
  
  return $CondivisioniCopyWith<$Res>(_self.condivisioni, (value) {
    return _then(_self.copyWith(condivisioni: value));
  });
}/// Create a copy of Profilo
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CartaCopyWith<$Res>? get cartaAnima {
    if (_self.cartaAnima == null) {
    return null;
  }

  return $CartaCopyWith<$Res>(_self.cartaAnima!, (value) {
    return _then(_self.copyWith(cartaAnima: value));
  });
}/// Create a copy of Profilo
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CartaCopyWith<$Res>? get cartaAnno {
    if (_self.cartaAnno == null) {
    return null;
  }

  return $CartaCopyWith<$Res>(_self.cartaAnno!, (value) {
    return _then(_self.copyWith(cartaAnno: value));
  });
}/// Create a copy of Profilo
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PosizioneAttualeCopyWith<$Res>? get posizione {
    if (_self.posizione == null) {
    return null;
  }

  return $PosizioneAttualeCopyWith<$Res>(_self.posizione!, (value) {
    return _then(_self.copyWith(posizione: value));
  });
}
}


/// @nodoc
mixin _$Dignita {

 String get elemento; num get punteggio; String get giudizio; List<RelazioneDignita> get relazioni;
/// Create a copy of Dignita
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DignitaCopyWith<Dignita> get copyWith => _$DignitaCopyWithImpl<Dignita>(this as Dignita, _$identity);

  /// Serializes this Dignita to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Dignita;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Dignita&&(identical(other.elemento, _this.elemento) || other.elemento == _this.elemento)&&(identical(other.punteggio, _this.punteggio) || other.punteggio == _this.punteggio)&&(identical(other.giudizio, _this.giudizio) || other.giudizio == _this.giudizio)&&const DeepCollectionEquality().equals(other.relazioni, _this.relazioni));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Dignita;
  return Object.hash(runtimeType,_this.elemento,_this.punteggio,_this.giudizio,const DeepCollectionEquality().hash(_this.relazioni));
}

@override
String toString() {
  final _this = this as Dignita;
  return 'Dignita(elemento: ${_this.elemento}, punteggio: ${_this.punteggio}, giudizio: ${_this.giudizio}, relazioni: ${_this.relazioni})';
}


}

/// @nodoc
abstract mixin class $DignitaCopyWith<$Res>  {
  factory $DignitaCopyWith(Dignita value, $Res Function(Dignita) _then) = _$DignitaCopyWithImpl;
@useResult
$Res call({
 String elemento, num punteggio, String giudizio, List<RelazioneDignita> relazioni
});




}
/// @nodoc
class _$DignitaCopyWithImpl<$Res>
    implements $DignitaCopyWith<$Res> {
  _$DignitaCopyWithImpl(this._self, this._then);

  final Dignita _self;
  final $Res Function(Dignita) _then;

/// Create a copy of Dignita
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? elemento = null,Object? punteggio = null,Object? giudizio = null,Object? relazioni = null,}) {
  return _then(Dignita(
elemento: null == elemento ? _self.elemento : elemento // ignore: cast_nullable_to_non_nullable
as String,punteggio: null == punteggio ? _self.punteggio : punteggio // ignore: cast_nullable_to_non_nullable
as num,giudizio: null == giudizio ? _self.giudizio : giudizio // ignore: cast_nullable_to_non_nullable
as String,relazioni: null == relazioni ? _self.relazioni : relazioni // ignore: cast_nullable_to_non_nullable
as List<RelazioneDignita>,
  ));
}

}


/// Adds pattern-matching-related methods to [Dignita].
extension DignitaPatterns on Dignita {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Dignita value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Dignita() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Dignita value)  $default,){
final _that = this;
switch (_that) {
case _Dignita():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Dignita value)?  $default,){
final _that = this;
switch (_that) {
case _Dignita() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String elemento,  num punteggio,  String giudizio,  List<RelazioneDignita> relazioni)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Dignita() when $default != null:
return $default(_that.elemento,_that.punteggio,_that.giudizio,_that.relazioni);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String elemento,  num punteggio,  String giudizio,  List<RelazioneDignita> relazioni)  $default,) {final _that = this;
switch (_that) {
case _Dignita():
return $default(_that.elemento,_that.punteggio,_that.giudizio,_that.relazioni);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String elemento,  num punteggio,  String giudizio,  List<RelazioneDignita> relazioni)?  $default,) {final _that = this;
switch (_that) {
case _Dignita() when $default != null:
return $default(_that.elemento,_that.punteggio,_that.giudizio,_that.relazioni);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Dignita implements Dignita {
  const _Dignita({required this.elemento, required this.punteggio, required this.giudizio,  List<RelazioneDignita> relazioni = const <RelazioneDignita>[]}): _relazioni = relazioni;
  factory _Dignita.fromJson(Map<String, dynamic> json) => _$DignitaFromJson(json);

@override final  String elemento;
@override final  num punteggio;
@override final  String giudizio;
 final  List<RelazioneDignita> _relazioni;
@override@JsonKey() List<RelazioneDignita> get relazioni {
  if (_relazioni is EqualUnmodifiableListView) return _relazioni;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_relazioni);
}


/// Create a copy of Dignita
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DignitaCopyWith<_Dignita> get copyWith => __$DignitaCopyWithImpl<_Dignita>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$DignitaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Dignita&&(identical(other.elemento, elemento) || other.elemento == elemento)&&(identical(other.punteggio, punteggio) || other.punteggio == punteggio)&&(identical(other.giudizio, giudizio) || other.giudizio == giudizio)&&const DeepCollectionEquality().equals(other.relazioni, _relazioni));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,elemento,punteggio,giudizio,const DeepCollectionEquality().hash(_relazioni));
}

@override
String toString() {
    return 'Dignita(elemento: $elemento, punteggio: $punteggio, giudizio: $giudizio, relazioni: $relazioni)';
}


}

/// @nodoc
abstract mixin class _$DignitaCopyWith<$Res> implements $DignitaCopyWith<$Res> {
  factory _$DignitaCopyWith(_Dignita value, $Res Function(_Dignita) _then) = __$DignitaCopyWithImpl;
@override @useResult
$Res call({
 String elemento, num punteggio, String giudizio, List<RelazioneDignita> relazioni
});




}
/// @nodoc
class __$DignitaCopyWithImpl<$Res>
    implements _$DignitaCopyWith<$Res> {
  __$DignitaCopyWithImpl(this._self, this._then);

  final _Dignita _self;
  final $Res Function(_Dignita) _then;

/// Create a copy of Dignita
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? elemento = null,Object? punteggio = null,Object? giudizio = null,Object? relazioni = null,}) {
  return _then(_Dignita(
elemento: null == elemento ? _self.elemento : elemento // ignore: cast_nullable_to_non_nullable
as String,punteggio: null == punteggio ? _self.punteggio : punteggio // ignore: cast_nullable_to_non_nullable
as num,giudizio: null == giudizio ? _self.giudizio : giudizio // ignore: cast_nullable_to_non_nullable
as String,relazioni: null == relazioni ? _self._relazioni : relazioni // ignore: cast_nullable_to_non_nullable
as List<RelazioneDignita>,
  ));
}


}


/// @nodoc
mixin _$RelazioneDignita {

 int get posizione; String get elemento; String get relazione;
/// Create a copy of RelazioneDignita
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RelazioneDignitaCopyWith<RelazioneDignita> get copyWith => _$RelazioneDignitaCopyWithImpl<RelazioneDignita>(this as RelazioneDignita, _$identity);

  /// Serializes this RelazioneDignita to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as RelazioneDignita;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RelazioneDignita&&(identical(other.posizione, _this.posizione) || other.posizione == _this.posizione)&&(identical(other.elemento, _this.elemento) || other.elemento == _this.elemento)&&(identical(other.relazione, _this.relazione) || other.relazione == _this.relazione));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as RelazioneDignita;
  return Object.hash(runtimeType,_this.posizione,_this.elemento,_this.relazione);
}

@override
String toString() {
  final _this = this as RelazioneDignita;
  return 'RelazioneDignita(posizione: ${_this.posizione}, elemento: ${_this.elemento}, relazione: ${_this.relazione})';
}


}

/// @nodoc
abstract mixin class $RelazioneDignitaCopyWith<$Res>  {
  factory $RelazioneDignitaCopyWith(RelazioneDignita value, $Res Function(RelazioneDignita) _then) = _$RelazioneDignitaCopyWithImpl;
@useResult
$Res call({
 int posizione, String elemento, String relazione
});




}
/// @nodoc
class _$RelazioneDignitaCopyWithImpl<$Res>
    implements $RelazioneDignitaCopyWith<$Res> {
  _$RelazioneDignitaCopyWithImpl(this._self, this._then);

  final RelazioneDignita _self;
  final $Res Function(RelazioneDignita) _then;

/// Create a copy of RelazioneDignita
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? posizione = null,Object? elemento = null,Object? relazione = null,}) {
  return _then(RelazioneDignita(
posizione: null == posizione ? _self.posizione : posizione // ignore: cast_nullable_to_non_nullable
as int,elemento: null == elemento ? _self.elemento : elemento // ignore: cast_nullable_to_non_nullable
as String,relazione: null == relazione ? _self.relazione : relazione // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [RelazioneDignita].
extension RelazioneDignitaPatterns on RelazioneDignita {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _RelazioneDignita value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _RelazioneDignita() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _RelazioneDignita value)  $default,){
final _that = this;
switch (_that) {
case _RelazioneDignita():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _RelazioneDignita value)?  $default,){
final _that = this;
switch (_that) {
case _RelazioneDignita() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int posizione,  String elemento,  String relazione)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _RelazioneDignita() when $default != null:
return $default(_that.posizione,_that.elemento,_that.relazione);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int posizione,  String elemento,  String relazione)  $default,) {final _that = this;
switch (_that) {
case _RelazioneDignita():
return $default(_that.posizione,_that.elemento,_that.relazione);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int posizione,  String elemento,  String relazione)?  $default,) {final _that = this;
switch (_that) {
case _RelazioneDignita() when $default != null:
return $default(_that.posizione,_that.elemento,_that.relazione);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _RelazioneDignita implements RelazioneDignita {
  const _RelazioneDignita({required this.posizione, required this.elemento, required this.relazione});
  factory _RelazioneDignita.fromJson(Map<String, dynamic> json) => _$RelazioneDignitaFromJson(json);

@override final  int posizione;
@override final  String elemento;
@override final  String relazione;

/// Create a copy of RelazioneDignita
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RelazioneDignitaCopyWith<_RelazioneDignita> get copyWith => __$RelazioneDignitaCopyWithImpl<_RelazioneDignita>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$RelazioneDignitaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _RelazioneDignita&&(identical(other.posizione, posizione) || other.posizione == posizione)&&(identical(other.elemento, elemento) || other.elemento == elemento)&&(identical(other.relazione, relazione) || other.relazione == relazione));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,posizione,elemento,relazione);
}

@override
String toString() {
    return 'RelazioneDignita(posizione: $posizione, elemento: $elemento, relazione: $relazione)';
}


}

/// @nodoc
abstract mixin class _$RelazioneDignitaCopyWith<$Res> implements $RelazioneDignitaCopyWith<$Res> {
  factory _$RelazioneDignitaCopyWith(_RelazioneDignita value, $Res Function(_RelazioneDignita) _then) = __$RelazioneDignitaCopyWithImpl;
@override @useResult
$Res call({
 int posizione, String elemento, String relazione
});




}
/// @nodoc
class __$RelazioneDignitaCopyWithImpl<$Res>
    implements _$RelazioneDignitaCopyWith<$Res> {
  __$RelazioneDignitaCopyWithImpl(this._self, this._then);

  final _RelazioneDignita _self;
  final $Res Function(_RelazioneDignita) _then;

/// Create a copy of RelazioneDignita
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? posizione = null,Object? elemento = null,Object? relazione = null,}) {
  return _then(_RelazioneDignita(
posizione: null == posizione ? _self.posizione : posizione // ignore: cast_nullable_to_non_nullable
as int,elemento: null == elemento ? _self.elemento : elemento // ignore: cast_nullable_to_non_nullable
as String,relazione: null == relazione ? _self.relazione : relazione // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$CartaPosata {

 int get posizione; bool get calcolata; bool get rivelata; Carta? get carta; bool? get rovescio; String? get interpretazione;
/// Create a copy of CartaPosata
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CartaPosataCopyWith<CartaPosata> get copyWith => _$CartaPosataCopyWithImpl<CartaPosata>(this as CartaPosata, _$identity);

  /// Serializes this CartaPosata to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as CartaPosata;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CartaPosata&&(identical(other.posizione, _this.posizione) || other.posizione == _this.posizione)&&(identical(other.calcolata, _this.calcolata) || other.calcolata == _this.calcolata)&&(identical(other.rivelata, _this.rivelata) || other.rivelata == _this.rivelata)&&(identical(other.carta, _this.carta) || other.carta == _this.carta)&&(identical(other.rovescio, _this.rovescio) || other.rovescio == _this.rovescio)&&(identical(other.interpretazione, _this.interpretazione) || other.interpretazione == _this.interpretazione));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as CartaPosata;
  return Object.hash(runtimeType,_this.posizione,_this.calcolata,_this.rivelata,_this.carta,_this.rovescio,_this.interpretazione);
}

@override
String toString() {
  final _this = this as CartaPosata;
  return 'CartaPosata(posizione: ${_this.posizione}, calcolata: ${_this.calcolata}, rivelata: ${_this.rivelata}, carta: ${_this.carta}, rovescio: ${_this.rovescio}, interpretazione: ${_this.interpretazione})';
}


}

/// @nodoc
abstract mixin class $CartaPosataCopyWith<$Res>  {
  factory $CartaPosataCopyWith(CartaPosata value, $Res Function(CartaPosata) _then) = _$CartaPosataCopyWithImpl;
@useResult
$Res call({
 int posizione, bool calcolata, bool rivelata, Carta? carta, bool? rovescio, String? interpretazione
});


$CartaCopyWith<$Res>? get carta;

}
/// @nodoc
class _$CartaPosataCopyWithImpl<$Res>
    implements $CartaPosataCopyWith<$Res> {
  _$CartaPosataCopyWithImpl(this._self, this._then);

  final CartaPosata _self;
  final $Res Function(CartaPosata) _then;

/// Create a copy of CartaPosata
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? posizione = null,Object? calcolata = null,Object? rivelata = null,Object? carta = freezed,Object? rovescio = freezed,Object? interpretazione = freezed,}) {
  return _then(CartaPosata(
posizione: null == posizione ? _self.posizione : posizione // ignore: cast_nullable_to_non_nullable
as int,calcolata: null == calcolata ? _self.calcolata : calcolata // ignore: cast_nullable_to_non_nullable
as bool,rivelata: null == rivelata ? _self.rivelata : rivelata // ignore: cast_nullable_to_non_nullable
as bool,carta: freezed == carta ? _self.carta : carta // ignore: cast_nullable_to_non_nullable
as Carta?,rovescio: freezed == rovescio ? _self.rovescio : rovescio // ignore: cast_nullable_to_non_nullable
as bool?,interpretazione: freezed == interpretazione ? _self.interpretazione : interpretazione // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}
/// Create a copy of CartaPosata
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CartaCopyWith<$Res>? get carta {
    if (_self.carta == null) {
    return null;
  }

  return $CartaCopyWith<$Res>(_self.carta!, (value) {
    return _then(_self.copyWith(carta: value));
  });
}
}


/// Adds pattern-matching-related methods to [CartaPosata].
extension CartaPosataPatterns on CartaPosata {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CartaPosata value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CartaPosata() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CartaPosata value)  $default,){
final _that = this;
switch (_that) {
case _CartaPosata():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CartaPosata value)?  $default,){
final _that = this;
switch (_that) {
case _CartaPosata() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int posizione,  bool calcolata,  bool rivelata,  Carta? carta,  bool? rovescio,  String? interpretazione)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CartaPosata() when $default != null:
return $default(_that.posizione,_that.calcolata,_that.rivelata,_that.carta,_that.rovescio,_that.interpretazione);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int posizione,  bool calcolata,  bool rivelata,  Carta? carta,  bool? rovescio,  String? interpretazione)  $default,) {final _that = this;
switch (_that) {
case _CartaPosata():
return $default(_that.posizione,_that.calcolata,_that.rivelata,_that.carta,_that.rovescio,_that.interpretazione);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int posizione,  bool calcolata,  bool rivelata,  Carta? carta,  bool? rovescio,  String? interpretazione)?  $default,) {final _that = this;
switch (_that) {
case _CartaPosata() when $default != null:
return $default(_that.posizione,_that.calcolata,_that.rivelata,_that.carta,_that.rovescio,_that.interpretazione);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CartaPosata implements CartaPosata {
  const _CartaPosata({required this.posizione, required this.calcolata, required this.rivelata, this.carta, this.rovescio, this.interpretazione});
  factory _CartaPosata.fromJson(Map<String, dynamic> json) => _$CartaPosataFromJson(json);

@override final  int posizione;
@override final  bool calcolata;
@override final  bool rivelata;
@override final  Carta? carta;
@override final  bool? rovescio;
@override final  String? interpretazione;

/// Create a copy of CartaPosata
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CartaPosataCopyWith<_CartaPosata> get copyWith => __$CartaPosataCopyWithImpl<_CartaPosata>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CartaPosataToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _CartaPosata&&(identical(other.posizione, posizione) || other.posizione == posizione)&&(identical(other.calcolata, calcolata) || other.calcolata == calcolata)&&(identical(other.rivelata, rivelata) || other.rivelata == rivelata)&&(identical(other.carta, carta) || other.carta == carta)&&(identical(other.rovescio, rovescio) || other.rovescio == rovescio)&&(identical(other.interpretazione, interpretazione) || other.interpretazione == interpretazione));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,posizione,calcolata,rivelata,carta,rovescio,interpretazione);
}

@override
String toString() {
    return 'CartaPosata(posizione: $posizione, calcolata: $calcolata, rivelata: $rivelata, carta: $carta, rovescio: $rovescio, interpretazione: $interpretazione)';
}


}

/// @nodoc
abstract mixin class _$CartaPosataCopyWith<$Res> implements $CartaPosataCopyWith<$Res> {
  factory _$CartaPosataCopyWith(_CartaPosata value, $Res Function(_CartaPosata) _then) = __$CartaPosataCopyWithImpl;
@override @useResult
$Res call({
 int posizione, bool calcolata, bool rivelata, Carta? carta, bool? rovescio, String? interpretazione
});


@override $CartaCopyWith<$Res>? get carta;

}
/// @nodoc
class __$CartaPosataCopyWithImpl<$Res>
    implements _$CartaPosataCopyWith<$Res> {
  __$CartaPosataCopyWithImpl(this._self, this._then);

  final _CartaPosata _self;
  final $Res Function(_CartaPosata) _then;

/// Create a copy of CartaPosata
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? posizione = null,Object? calcolata = null,Object? rivelata = null,Object? carta = freezed,Object? rovescio = freezed,Object? interpretazione = freezed,}) {
  return _then(_CartaPosata(
posizione: null == posizione ? _self.posizione : posizione // ignore: cast_nullable_to_non_nullable
as int,calcolata: null == calcolata ? _self.calcolata : calcolata // ignore: cast_nullable_to_non_nullable
as bool,rivelata: null == rivelata ? _self.rivelata : rivelata // ignore: cast_nullable_to_non_nullable
as bool,carta: freezed == carta ? _self.carta : carta // ignore: cast_nullable_to_non_nullable
as Carta?,rovescio: freezed == rovescio ? _self.rovescio : rovescio // ignore: cast_nullable_to_non_nullable
as bool?,interpretazione: freezed == interpretazione ? _self.interpretazione : interpretazione // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of CartaPosata
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CartaCopyWith<$Res>? get carta {
    if (_self.carta == null) {
    return null;
  }

  return $CartaCopyWith<$Res>(_self.carta!, (value) {
    return _then(_self.copyWith(carta: value));
  });
}
}


/// @nodoc
mixin _$TurnoIntervista {

 String get ruolo; String get testo; int get ordine;
/// Create a copy of TurnoIntervista
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$TurnoIntervistaCopyWith<TurnoIntervista> get copyWith => _$TurnoIntervistaCopyWithImpl<TurnoIntervista>(this as TurnoIntervista, _$identity);

  /// Serializes this TurnoIntervista to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as TurnoIntervista;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is TurnoIntervista&&(identical(other.ruolo, _this.ruolo) || other.ruolo == _this.ruolo)&&(identical(other.testo, _this.testo) || other.testo == _this.testo)&&(identical(other.ordine, _this.ordine) || other.ordine == _this.ordine));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as TurnoIntervista;
  return Object.hash(runtimeType,_this.ruolo,_this.testo,_this.ordine);
}

@override
String toString() {
  final _this = this as TurnoIntervista;
  return 'TurnoIntervista(ruolo: ${_this.ruolo}, testo: ${_this.testo}, ordine: ${_this.ordine})';
}


}

/// @nodoc
abstract mixin class $TurnoIntervistaCopyWith<$Res>  {
  factory $TurnoIntervistaCopyWith(TurnoIntervista value, $Res Function(TurnoIntervista) _then) = _$TurnoIntervistaCopyWithImpl;
@useResult
$Res call({
 String ruolo, String testo, int ordine
});




}
/// @nodoc
class _$TurnoIntervistaCopyWithImpl<$Res>
    implements $TurnoIntervistaCopyWith<$Res> {
  _$TurnoIntervistaCopyWithImpl(this._self, this._then);

  final TurnoIntervista _self;
  final $Res Function(TurnoIntervista) _then;

/// Create a copy of TurnoIntervista
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? ruolo = null,Object? testo = null,Object? ordine = null,}) {
  return _then(TurnoIntervista(
ruolo: null == ruolo ? _self.ruolo : ruolo // ignore: cast_nullable_to_non_nullable
as String,testo: null == testo ? _self.testo : testo // ignore: cast_nullable_to_non_nullable
as String,ordine: null == ordine ? _self.ordine : ordine // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [TurnoIntervista].
extension TurnoIntervistaPatterns on TurnoIntervista {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _TurnoIntervista value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _TurnoIntervista() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _TurnoIntervista value)  $default,){
final _that = this;
switch (_that) {
case _TurnoIntervista():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _TurnoIntervista value)?  $default,){
final _that = this;
switch (_that) {
case _TurnoIntervista() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String ruolo,  String testo,  int ordine)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _TurnoIntervista() when $default != null:
return $default(_that.ruolo,_that.testo,_that.ordine);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String ruolo,  String testo,  int ordine)  $default,) {final _that = this;
switch (_that) {
case _TurnoIntervista():
return $default(_that.ruolo,_that.testo,_that.ordine);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String ruolo,  String testo,  int ordine)?  $default,) {final _that = this;
switch (_that) {
case _TurnoIntervista() when $default != null:
return $default(_that.ruolo,_that.testo,_that.ordine);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _TurnoIntervista implements TurnoIntervista {
  const _TurnoIntervista({required this.ruolo, required this.testo, required this.ordine});
  factory _TurnoIntervista.fromJson(Map<String, dynamic> json) => _$TurnoIntervistaFromJson(json);

@override final  String ruolo;
@override final  String testo;
@override final  int ordine;

/// Create a copy of TurnoIntervista
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$TurnoIntervistaCopyWith<_TurnoIntervista> get copyWith => __$TurnoIntervistaCopyWithImpl<_TurnoIntervista>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$TurnoIntervistaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _TurnoIntervista&&(identical(other.ruolo, ruolo) || other.ruolo == ruolo)&&(identical(other.testo, testo) || other.testo == testo)&&(identical(other.ordine, ordine) || other.ordine == ordine));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,ruolo,testo,ordine);
}

@override
String toString() {
    return 'TurnoIntervista(ruolo: $ruolo, testo: $testo, ordine: $ordine)';
}


}

/// @nodoc
abstract mixin class _$TurnoIntervistaCopyWith<$Res> implements $TurnoIntervistaCopyWith<$Res> {
  factory _$TurnoIntervistaCopyWith(_TurnoIntervista value, $Res Function(_TurnoIntervista) _then) = __$TurnoIntervistaCopyWithImpl;
@override @useResult
$Res call({
 String ruolo, String testo, int ordine
});




}
/// @nodoc
class __$TurnoIntervistaCopyWithImpl<$Res>
    implements _$TurnoIntervistaCopyWith<$Res> {
  __$TurnoIntervistaCopyWithImpl(this._self, this._then);

  final _TurnoIntervista _self;
  final $Res Function(_TurnoIntervista) _then;

/// Create a copy of TurnoIntervista
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? ruolo = null,Object? testo = null,Object? ordine = null,}) {
  return _then(_TurnoIntervista(
ruolo: null == ruolo ? _self.ruolo : ruolo // ignore: cast_nullable_to_non_nullable
as String,testo: null == testo ? _self.testo : testo // ignore: cast_nullable_to_non_nullable
as String,ordine: null == ordine ? _self.ordine : ordine // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$PersonaTu {

 String? get genere; String? get genereAltro; bool get trans; String get nascita;
/// Create a copy of PersonaTu
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PersonaTuCopyWith<PersonaTu> get copyWith => _$PersonaTuCopyWithImpl<PersonaTu>(this as PersonaTu, _$identity);

  /// Serializes this PersonaTu to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as PersonaTu;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PersonaTu&&(identical(other.genere, _this.genere) || other.genere == _this.genere)&&(identical(other.genereAltro, _this.genereAltro) || other.genereAltro == _this.genereAltro)&&(identical(other.trans, _this.trans) || other.trans == _this.trans)&&(identical(other.nascita, _this.nascita) || other.nascita == _this.nascita));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as PersonaTu;
  return Object.hash(runtimeType,_this.genere,_this.genereAltro,_this.trans,_this.nascita);
}

@override
String toString() {
  final _this = this as PersonaTu;
  return 'PersonaTu(genere: ${_this.genere}, genereAltro: ${_this.genereAltro}, trans: ${_this.trans}, nascita: ${_this.nascita})';
}


}

/// @nodoc
abstract mixin class $PersonaTuCopyWith<$Res>  {
  factory $PersonaTuCopyWith(PersonaTu value, $Res Function(PersonaTu) _then) = _$PersonaTuCopyWithImpl;
@useResult
$Res call({
 String? genere, String? genereAltro, bool trans, String nascita
});




}
/// @nodoc
class _$PersonaTuCopyWithImpl<$Res>
    implements $PersonaTuCopyWith<$Res> {
  _$PersonaTuCopyWithImpl(this._self, this._then);

  final PersonaTu _self;
  final $Res Function(PersonaTu) _then;

/// Create a copy of PersonaTu
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? genere = freezed,Object? genereAltro = freezed,Object? trans = null,Object? nascita = null,}) {
  return _then(PersonaTu(
genere: freezed == genere ? _self.genere : genere // ignore: cast_nullable_to_non_nullable
as String?,genereAltro: freezed == genereAltro ? _self.genereAltro : genereAltro // ignore: cast_nullable_to_non_nullable
as String?,trans: null == trans ? _self.trans : trans // ignore: cast_nullable_to_non_nullable
as bool,nascita: null == nascita ? _self.nascita : nascita // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [PersonaTu].
extension PersonaTuPatterns on PersonaTu {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PersonaTu value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PersonaTu() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PersonaTu value)  $default,){
final _that = this;
switch (_that) {
case _PersonaTu():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PersonaTu value)?  $default,){
final _that = this;
switch (_that) {
case _PersonaTu() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? genere,  String? genereAltro,  bool trans,  String nascita)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PersonaTu() when $default != null:
return $default(_that.genere,_that.genereAltro,_that.trans,_that.nascita);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? genere,  String? genereAltro,  bool trans,  String nascita)  $default,) {final _that = this;
switch (_that) {
case _PersonaTu():
return $default(_that.genere,_that.genereAltro,_that.trans,_that.nascita);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? genere,  String? genereAltro,  bool trans,  String nascita)?  $default,) {final _that = this;
switch (_that) {
case _PersonaTu() when $default != null:
return $default(_that.genere,_that.genereAltro,_that.trans,_that.nascita);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _PersonaTu implements PersonaTu {
  const _PersonaTu({this.genere, this.genereAltro, this.trans = false, required this.nascita});
  factory _PersonaTu.fromJson(Map<String, dynamic> json) => _$PersonaTuFromJson(json);

@override final  String? genere;
@override final  String? genereAltro;
@override@JsonKey() final  bool trans;
@override final  String nascita;

/// Create a copy of PersonaTu
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PersonaTuCopyWith<_PersonaTu> get copyWith => __$PersonaTuCopyWithImpl<_PersonaTu>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PersonaTuToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _PersonaTu&&(identical(other.genere, genere) || other.genere == genere)&&(identical(other.genereAltro, genereAltro) || other.genereAltro == genereAltro)&&(identical(other.trans, trans) || other.trans == trans)&&(identical(other.nascita, nascita) || other.nascita == nascita));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,genere,genereAltro,trans,nascita);
}

@override
String toString() {
    return 'PersonaTu(genere: $genere, genereAltro: $genereAltro, trans: $trans, nascita: $nascita)';
}


}

/// @nodoc
abstract mixin class _$PersonaTuCopyWith<$Res> implements $PersonaTuCopyWith<$Res> {
  factory _$PersonaTuCopyWith(_PersonaTu value, $Res Function(_PersonaTu) _then) = __$PersonaTuCopyWithImpl;
@override @useResult
$Res call({
 String? genere, String? genereAltro, bool trans, String nascita
});




}
/// @nodoc
class __$PersonaTuCopyWithImpl<$Res>
    implements _$PersonaTuCopyWith<$Res> {
  __$PersonaTuCopyWithImpl(this._self, this._then);

  final _PersonaTu _self;
  final $Res Function(_PersonaTu) _then;

/// Create a copy of PersonaTu
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? genere = freezed,Object? genereAltro = freezed,Object? trans = null,Object? nascita = null,}) {
  return _then(_PersonaTu(
genere: freezed == genere ? _self.genere : genere // ignore: cast_nullable_to_non_nullable
as String?,genereAltro: freezed == genereAltro ? _self.genereAltro : genereAltro // ignore: cast_nullable_to_non_nullable
as String?,trans: null == trans ? _self.trans : trans // ignore: cast_nullable_to_non_nullable
as bool,nascita: null == nascita ? _self.nascita : nascita // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$PersoneLettura {

 int get v; PersonaTu get tu; PersonaSalvata get partner;
/// Create a copy of PersoneLettura
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PersoneLetturaCopyWith<PersoneLettura> get copyWith => _$PersoneLetturaCopyWithImpl<PersoneLettura>(this as PersoneLettura, _$identity);

  /// Serializes this PersoneLettura to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as PersoneLettura;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PersoneLettura&&(identical(other.v, _this.v) || other.v == _this.v)&&(identical(other.tu, _this.tu) || other.tu == _this.tu)&&(identical(other.partner, _this.partner) || other.partner == _this.partner));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as PersoneLettura;
  return Object.hash(runtimeType,_this.v,_this.tu,_this.partner);
}

@override
String toString() {
  final _this = this as PersoneLettura;
  return 'PersoneLettura(v: ${_this.v}, tu: ${_this.tu}, partner: ${_this.partner})';
}


}

/// @nodoc
abstract mixin class $PersoneLetturaCopyWith<$Res>  {
  factory $PersoneLetturaCopyWith(PersoneLettura value, $Res Function(PersoneLettura) _then) = _$PersoneLetturaCopyWithImpl;
@useResult
$Res call({
 int v, PersonaTu tu, PersonaSalvata partner
});


$PersonaTuCopyWith<$Res> get tu;$PersonaSalvataCopyWith<$Res> get partner;

}
/// @nodoc
class _$PersoneLetturaCopyWithImpl<$Res>
    implements $PersoneLetturaCopyWith<$Res> {
  _$PersoneLetturaCopyWithImpl(this._self, this._then);

  final PersoneLettura _self;
  final $Res Function(PersoneLettura) _then;

/// Create a copy of PersoneLettura
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? v = null,Object? tu = null,Object? partner = null,}) {
  return _then(PersoneLettura(
v: null == v ? _self.v : v // ignore: cast_nullable_to_non_nullable
as int,tu: null == tu ? _self.tu : tu // ignore: cast_nullable_to_non_nullable
as PersonaTu,partner: null == partner ? _self.partner : partner // ignore: cast_nullable_to_non_nullable
as PersonaSalvata,
  ));
}
/// Create a copy of PersoneLettura
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PersonaTuCopyWith<$Res> get tu {
  
  return $PersonaTuCopyWith<$Res>(_self.tu, (value) {
    return _then(_self.copyWith(tu: value));
  });
}/// Create a copy of PersoneLettura
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PersonaSalvataCopyWith<$Res> get partner {
  
  return $PersonaSalvataCopyWith<$Res>(_self.partner, (value) {
    return _then(_self.copyWith(partner: value));
  });
}
}


/// Adds pattern-matching-related methods to [PersoneLettura].
extension PersoneLetturaPatterns on PersoneLettura {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PersoneLettura value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PersoneLettura() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PersoneLettura value)  $default,){
final _that = this;
switch (_that) {
case _PersoneLettura():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PersoneLettura value)?  $default,){
final _that = this;
switch (_that) {
case _PersoneLettura() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int v,  PersonaTu tu,  PersonaSalvata partner)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PersoneLettura() when $default != null:
return $default(_that.v,_that.tu,_that.partner);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int v,  PersonaTu tu,  PersonaSalvata partner)  $default,) {final _that = this;
switch (_that) {
case _PersoneLettura():
return $default(_that.v,_that.tu,_that.partner);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int v,  PersonaTu tu,  PersonaSalvata partner)?  $default,) {final _that = this;
switch (_that) {
case _PersoneLettura() when $default != null:
return $default(_that.v,_that.tu,_that.partner);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _PersoneLettura implements PersoneLettura {
  const _PersoneLettura({this.v = 1, required this.tu, required this.partner});
  factory _PersoneLettura.fromJson(Map<String, dynamic> json) => _$PersoneLetturaFromJson(json);

@override@JsonKey() final  int v;
@override final  PersonaTu tu;
@override final  PersonaSalvata partner;

/// Create a copy of PersoneLettura
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PersoneLetturaCopyWith<_PersoneLettura> get copyWith => __$PersoneLetturaCopyWithImpl<_PersoneLettura>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PersoneLetturaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _PersoneLettura&&(identical(other.v, v) || other.v == v)&&(identical(other.tu, tu) || other.tu == tu)&&(identical(other.partner, partner) || other.partner == partner));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,v,tu,partner);
}

@override
String toString() {
    return 'PersoneLettura(v: $v, tu: $tu, partner: $partner)';
}


}

/// @nodoc
abstract mixin class _$PersoneLetturaCopyWith<$Res> implements $PersoneLetturaCopyWith<$Res> {
  factory _$PersoneLetturaCopyWith(_PersoneLettura value, $Res Function(_PersoneLettura) _then) = __$PersoneLetturaCopyWithImpl;
@override @useResult
$Res call({
 int v, PersonaTu tu, PersonaSalvata partner
});


@override $PersonaTuCopyWith<$Res> get tu;@override $PersonaSalvataCopyWith<$Res> get partner;

}
/// @nodoc
class __$PersoneLetturaCopyWithImpl<$Res>
    implements _$PersoneLetturaCopyWith<$Res> {
  __$PersoneLetturaCopyWithImpl(this._self, this._then);

  final _PersoneLettura _self;
  final $Res Function(_PersoneLettura) _then;

/// Create a copy of PersoneLettura
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? v = null,Object? tu = null,Object? partner = null,}) {
  return _then(_PersoneLettura(
v: null == v ? _self.v : v // ignore: cast_nullable_to_non_nullable
as int,tu: null == tu ? _self.tu : tu // ignore: cast_nullable_to_non_nullable
as PersonaTu,partner: null == partner ? _self.partner : partner // ignore: cast_nullable_to_non_nullable
as PersonaSalvata,
  ));
}

/// Create a copy of PersoneLettura
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PersonaTuCopyWith<$Res> get tu {
  
  return $PersonaTuCopyWith<$Res>(_self.tu, (value) {
    return _then(_self.copyWith(tu: value));
  });
}/// Create a copy of PersoneLettura
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PersonaSalvataCopyWith<$Res> get partner {
  
  return $PersonaSalvataCopyWith<$Res>(_self.partner, (value) {
    return _then(_self.copyWith(partner: value));
  });
}
}


/// @nodoc
mixin _$SegnoCalcolato {

 String get codice; String get elemento; String get modalita; bool get cuspide; String? get vicino;
/// Create a copy of SegnoCalcolato
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SegnoCalcolatoCopyWith<SegnoCalcolato> get copyWith => _$SegnoCalcolatoCopyWithImpl<SegnoCalcolato>(this as SegnoCalcolato, _$identity);

  /// Serializes this SegnoCalcolato to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as SegnoCalcolato;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SegnoCalcolato&&(identical(other.codice, _this.codice) || other.codice == _this.codice)&&(identical(other.elemento, _this.elemento) || other.elemento == _this.elemento)&&(identical(other.modalita, _this.modalita) || other.modalita == _this.modalita)&&(identical(other.cuspide, _this.cuspide) || other.cuspide == _this.cuspide)&&(identical(other.vicino, _this.vicino) || other.vicino == _this.vicino));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as SegnoCalcolato;
  return Object.hash(runtimeType,_this.codice,_this.elemento,_this.modalita,_this.cuspide,_this.vicino);
}

@override
String toString() {
  final _this = this as SegnoCalcolato;
  return 'SegnoCalcolato(codice: ${_this.codice}, elemento: ${_this.elemento}, modalita: ${_this.modalita}, cuspide: ${_this.cuspide}, vicino: ${_this.vicino})';
}


}

/// @nodoc
abstract mixin class $SegnoCalcolatoCopyWith<$Res>  {
  factory $SegnoCalcolatoCopyWith(SegnoCalcolato value, $Res Function(SegnoCalcolato) _then) = _$SegnoCalcolatoCopyWithImpl;
@useResult
$Res call({
 String codice, String elemento, String modalita, bool cuspide, String? vicino
});




}
/// @nodoc
class _$SegnoCalcolatoCopyWithImpl<$Res>
    implements $SegnoCalcolatoCopyWith<$Res> {
  _$SegnoCalcolatoCopyWithImpl(this._self, this._then);

  final SegnoCalcolato _self;
  final $Res Function(SegnoCalcolato) _then;

/// Create a copy of SegnoCalcolato
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? codice = null,Object? elemento = null,Object? modalita = null,Object? cuspide = null,Object? vicino = freezed,}) {
  return _then(SegnoCalcolato(
codice: null == codice ? _self.codice : codice // ignore: cast_nullable_to_non_nullable
as String,elemento: null == elemento ? _self.elemento : elemento // ignore: cast_nullable_to_non_nullable
as String,modalita: null == modalita ? _self.modalita : modalita // ignore: cast_nullable_to_non_nullable
as String,cuspide: null == cuspide ? _self.cuspide : cuspide // ignore: cast_nullable_to_non_nullable
as bool,vicino: freezed == vicino ? _self.vicino : vicino // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [SegnoCalcolato].
extension SegnoCalcolatoPatterns on SegnoCalcolato {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _SegnoCalcolato value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _SegnoCalcolato() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _SegnoCalcolato value)  $default,){
final _that = this;
switch (_that) {
case _SegnoCalcolato():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _SegnoCalcolato value)?  $default,){
final _that = this;
switch (_that) {
case _SegnoCalcolato() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String codice,  String elemento,  String modalita,  bool cuspide,  String? vicino)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _SegnoCalcolato() when $default != null:
return $default(_that.codice,_that.elemento,_that.modalita,_that.cuspide,_that.vicino);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String codice,  String elemento,  String modalita,  bool cuspide,  String? vicino)  $default,) {final _that = this;
switch (_that) {
case _SegnoCalcolato():
return $default(_that.codice,_that.elemento,_that.modalita,_that.cuspide,_that.vicino);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String codice,  String elemento,  String modalita,  bool cuspide,  String? vicino)?  $default,) {final _that = this;
switch (_that) {
case _SegnoCalcolato() when $default != null:
return $default(_that.codice,_that.elemento,_that.modalita,_that.cuspide,_that.vicino);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _SegnoCalcolato implements SegnoCalcolato {
  const _SegnoCalcolato({required this.codice, required this.elemento, required this.modalita, this.cuspide = false, this.vicino});
  factory _SegnoCalcolato.fromJson(Map<String, dynamic> json) => _$SegnoCalcolatoFromJson(json);

@override final  String codice;
@override final  String elemento;
@override final  String modalita;
@override@JsonKey() final  bool cuspide;
@override final  String? vicino;

/// Create a copy of SegnoCalcolato
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SegnoCalcolatoCopyWith<_SegnoCalcolato> get copyWith => __$SegnoCalcolatoCopyWithImpl<_SegnoCalcolato>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SegnoCalcolatoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _SegnoCalcolato&&(identical(other.codice, codice) || other.codice == codice)&&(identical(other.elemento, elemento) || other.elemento == elemento)&&(identical(other.modalita, modalita) || other.modalita == modalita)&&(identical(other.cuspide, cuspide) || other.cuspide == cuspide)&&(identical(other.vicino, vicino) || other.vicino == vicino));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,codice,elemento,modalita,cuspide,vicino);
}

@override
String toString() {
    return 'SegnoCalcolato(codice: $codice, elemento: $elemento, modalita: $modalita, cuspide: $cuspide, vicino: $vicino)';
}


}

/// @nodoc
abstract mixin class _$SegnoCalcolatoCopyWith<$Res> implements $SegnoCalcolatoCopyWith<$Res> {
  factory _$SegnoCalcolatoCopyWith(_SegnoCalcolato value, $Res Function(_SegnoCalcolato) _then) = __$SegnoCalcolatoCopyWithImpl;
@override @useResult
$Res call({
 String codice, String elemento, String modalita, bool cuspide, String? vicino
});




}
/// @nodoc
class __$SegnoCalcolatoCopyWithImpl<$Res>
    implements _$SegnoCalcolatoCopyWith<$Res> {
  __$SegnoCalcolatoCopyWithImpl(this._self, this._then);

  final _SegnoCalcolato _self;
  final $Res Function(_SegnoCalcolato) _then;

/// Create a copy of SegnoCalcolato
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? codice = null,Object? elemento = null,Object? modalita = null,Object? cuspide = null,Object? vicino = freezed,}) {
  return _then(_SegnoCalcolato(
codice: null == codice ? _self.codice : codice // ignore: cast_nullable_to_non_nullable
as String,elemento: null == elemento ? _self.elemento : elemento // ignore: cast_nullable_to_non_nullable
as String,modalita: null == modalita ? _self.modalita : modalita // ignore: cast_nullable_to_non_nullable
as String,cuspide: null == cuspide ? _self.cuspide : cuspide // ignore: cast_nullable_to_non_nullable
as bool,vicino: freezed == vicino ? _self.vicino : vicino // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$SegniCoppia {

 SegnoCalcolato get tu; SegnoCalcolato get partner;
/// Create a copy of SegniCoppia
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SegniCoppiaCopyWith<SegniCoppia> get copyWith => _$SegniCoppiaCopyWithImpl<SegniCoppia>(this as SegniCoppia, _$identity);

  /// Serializes this SegniCoppia to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as SegniCoppia;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SegniCoppia&&(identical(other.tu, _this.tu) || other.tu == _this.tu)&&(identical(other.partner, _this.partner) || other.partner == _this.partner));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as SegniCoppia;
  return Object.hash(runtimeType,_this.tu,_this.partner);
}

@override
String toString() {
  final _this = this as SegniCoppia;
  return 'SegniCoppia(tu: ${_this.tu}, partner: ${_this.partner})';
}


}

/// @nodoc
abstract mixin class $SegniCoppiaCopyWith<$Res>  {
  factory $SegniCoppiaCopyWith(SegniCoppia value, $Res Function(SegniCoppia) _then) = _$SegniCoppiaCopyWithImpl;
@useResult
$Res call({
 SegnoCalcolato tu, SegnoCalcolato partner
});


$SegnoCalcolatoCopyWith<$Res> get tu;$SegnoCalcolatoCopyWith<$Res> get partner;

}
/// @nodoc
class _$SegniCoppiaCopyWithImpl<$Res>
    implements $SegniCoppiaCopyWith<$Res> {
  _$SegniCoppiaCopyWithImpl(this._self, this._then);

  final SegniCoppia _self;
  final $Res Function(SegniCoppia) _then;

/// Create a copy of SegniCoppia
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? tu = null,Object? partner = null,}) {
  return _then(SegniCoppia(
tu: null == tu ? _self.tu : tu // ignore: cast_nullable_to_non_nullable
as SegnoCalcolato,partner: null == partner ? _self.partner : partner // ignore: cast_nullable_to_non_nullable
as SegnoCalcolato,
  ));
}
/// Create a copy of SegniCoppia
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$SegnoCalcolatoCopyWith<$Res> get tu {
  
  return $SegnoCalcolatoCopyWith<$Res>(_self.tu, (value) {
    return _then(_self.copyWith(tu: value));
  });
}/// Create a copy of SegniCoppia
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$SegnoCalcolatoCopyWith<$Res> get partner {
  
  return $SegnoCalcolatoCopyWith<$Res>(_self.partner, (value) {
    return _then(_self.copyWith(partner: value));
  });
}
}


/// Adds pattern-matching-related methods to [SegniCoppia].
extension SegniCoppiaPatterns on SegniCoppia {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _SegniCoppia value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _SegniCoppia() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _SegniCoppia value)  $default,){
final _that = this;
switch (_that) {
case _SegniCoppia():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _SegniCoppia value)?  $default,){
final _that = this;
switch (_that) {
case _SegniCoppia() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( SegnoCalcolato tu,  SegnoCalcolato partner)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _SegniCoppia() when $default != null:
return $default(_that.tu,_that.partner);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( SegnoCalcolato tu,  SegnoCalcolato partner)  $default,) {final _that = this;
switch (_that) {
case _SegniCoppia():
return $default(_that.tu,_that.partner);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( SegnoCalcolato tu,  SegnoCalcolato partner)?  $default,) {final _that = this;
switch (_that) {
case _SegniCoppia() when $default != null:
return $default(_that.tu,_that.partner);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _SegniCoppia implements SegniCoppia {
  const _SegniCoppia({required this.tu, required this.partner});
  factory _SegniCoppia.fromJson(Map<String, dynamic> json) => _$SegniCoppiaFromJson(json);

@override final  SegnoCalcolato tu;
@override final  SegnoCalcolato partner;

/// Create a copy of SegniCoppia
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SegniCoppiaCopyWith<_SegniCoppia> get copyWith => __$SegniCoppiaCopyWithImpl<_SegniCoppia>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SegniCoppiaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _SegniCoppia&&(identical(other.tu, tu) || other.tu == tu)&&(identical(other.partner, partner) || other.partner == partner));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,tu,partner);
}

@override
String toString() {
    return 'SegniCoppia(tu: $tu, partner: $partner)';
}


}

/// @nodoc
abstract mixin class _$SegniCoppiaCopyWith<$Res> implements $SegniCoppiaCopyWith<$Res> {
  factory _$SegniCoppiaCopyWith(_SegniCoppia value, $Res Function(_SegniCoppia) _then) = __$SegniCoppiaCopyWithImpl;
@override @useResult
$Res call({
 SegnoCalcolato tu, SegnoCalcolato partner
});


@override $SegnoCalcolatoCopyWith<$Res> get tu;@override $SegnoCalcolatoCopyWith<$Res> get partner;

}
/// @nodoc
class __$SegniCoppiaCopyWithImpl<$Res>
    implements _$SegniCoppiaCopyWith<$Res> {
  __$SegniCoppiaCopyWithImpl(this._self, this._then);

  final _SegniCoppia _self;
  final $Res Function(_SegniCoppia) _then;

/// Create a copy of SegniCoppia
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? tu = null,Object? partner = null,}) {
  return _then(_SegniCoppia(
tu: null == tu ? _self.tu : tu // ignore: cast_nullable_to_non_nullable
as SegnoCalcolato,partner: null == partner ? _self.partner : partner // ignore: cast_nullable_to_non_nullable
as SegnoCalcolato,
  ));
}

/// Create a copy of SegniCoppia
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$SegnoCalcolatoCopyWith<$Res> get tu {
  
  return $SegnoCalcolatoCopyWith<$Res>(_self.tu, (value) {
    return _then(_self.copyWith(tu: value));
  });
}/// Create a copy of SegniCoppia
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$SegnoCalcolatoCopyWith<$Res> get partner {
  
  return $SegnoCalcolatoCopyWith<$Res>(_self.partner, (value) {
    return _then(_self.copyWith(partner: value));
  });
}
}


/// @nodoc
mixin _$Compatibilita {

 SegniCoppia get segni; int get distanza; String get aspetto; String get relazioneElementi; bool get stessaModalita; String get armonia; Carta get cartaCoppia; Carta get cartaAnimaTu; Carta get cartaAnimaPartner;
/// Create a copy of Compatibilita
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CompatibilitaCopyWith<Compatibilita> get copyWith => _$CompatibilitaCopyWithImpl<Compatibilita>(this as Compatibilita, _$identity);

  /// Serializes this Compatibilita to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Compatibilita;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Compatibilita&&(identical(other.segni, _this.segni) || other.segni == _this.segni)&&(identical(other.distanza, _this.distanza) || other.distanza == _this.distanza)&&(identical(other.aspetto, _this.aspetto) || other.aspetto == _this.aspetto)&&(identical(other.relazioneElementi, _this.relazioneElementi) || other.relazioneElementi == _this.relazioneElementi)&&(identical(other.stessaModalita, _this.stessaModalita) || other.stessaModalita == _this.stessaModalita)&&(identical(other.armonia, _this.armonia) || other.armonia == _this.armonia)&&(identical(other.cartaCoppia, _this.cartaCoppia) || other.cartaCoppia == _this.cartaCoppia)&&(identical(other.cartaAnimaTu, _this.cartaAnimaTu) || other.cartaAnimaTu == _this.cartaAnimaTu)&&(identical(other.cartaAnimaPartner, _this.cartaAnimaPartner) || other.cartaAnimaPartner == _this.cartaAnimaPartner));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Compatibilita;
  return Object.hash(runtimeType,_this.segni,_this.distanza,_this.aspetto,_this.relazioneElementi,_this.stessaModalita,_this.armonia,_this.cartaCoppia,_this.cartaAnimaTu,_this.cartaAnimaPartner);
}

@override
String toString() {
  final _this = this as Compatibilita;
  return 'Compatibilita(segni: ${_this.segni}, distanza: ${_this.distanza}, aspetto: ${_this.aspetto}, relazioneElementi: ${_this.relazioneElementi}, stessaModalita: ${_this.stessaModalita}, armonia: ${_this.armonia}, cartaCoppia: ${_this.cartaCoppia}, cartaAnimaTu: ${_this.cartaAnimaTu}, cartaAnimaPartner: ${_this.cartaAnimaPartner})';
}


}

/// @nodoc
abstract mixin class $CompatibilitaCopyWith<$Res>  {
  factory $CompatibilitaCopyWith(Compatibilita value, $Res Function(Compatibilita) _then) = _$CompatibilitaCopyWithImpl;
@useResult
$Res call({
 SegniCoppia segni, int distanza, String aspetto, String relazioneElementi, bool stessaModalita, String armonia, Carta cartaCoppia, Carta cartaAnimaTu, Carta cartaAnimaPartner
});


$SegniCoppiaCopyWith<$Res> get segni;$CartaCopyWith<$Res> get cartaCoppia;$CartaCopyWith<$Res> get cartaAnimaTu;$CartaCopyWith<$Res> get cartaAnimaPartner;

}
/// @nodoc
class _$CompatibilitaCopyWithImpl<$Res>
    implements $CompatibilitaCopyWith<$Res> {
  _$CompatibilitaCopyWithImpl(this._self, this._then);

  final Compatibilita _self;
  final $Res Function(Compatibilita) _then;

/// Create a copy of Compatibilita
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? segni = null,Object? distanza = null,Object? aspetto = null,Object? relazioneElementi = null,Object? stessaModalita = null,Object? armonia = null,Object? cartaCoppia = null,Object? cartaAnimaTu = null,Object? cartaAnimaPartner = null,}) {
  return _then(Compatibilita(
segni: null == segni ? _self.segni : segni // ignore: cast_nullable_to_non_nullable
as SegniCoppia,distanza: null == distanza ? _self.distanza : distanza // ignore: cast_nullable_to_non_nullable
as int,aspetto: null == aspetto ? _self.aspetto : aspetto // ignore: cast_nullable_to_non_nullable
as String,relazioneElementi: null == relazioneElementi ? _self.relazioneElementi : relazioneElementi // ignore: cast_nullable_to_non_nullable
as String,stessaModalita: null == stessaModalita ? _self.stessaModalita : stessaModalita // ignore: cast_nullable_to_non_nullable
as bool,armonia: null == armonia ? _self.armonia : armonia // ignore: cast_nullable_to_non_nullable
as String,cartaCoppia: null == cartaCoppia ? _self.cartaCoppia : cartaCoppia // ignore: cast_nullable_to_non_nullable
as Carta,cartaAnimaTu: null == cartaAnimaTu ? _self.cartaAnimaTu : cartaAnimaTu // ignore: cast_nullable_to_non_nullable
as Carta,cartaAnimaPartner: null == cartaAnimaPartner ? _self.cartaAnimaPartner : cartaAnimaPartner // ignore: cast_nullable_to_non_nullable
as Carta,
  ));
}
/// Create a copy of Compatibilita
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$SegniCoppiaCopyWith<$Res> get segni {
  
  return $SegniCoppiaCopyWith<$Res>(_self.segni, (value) {
    return _then(_self.copyWith(segni: value));
  });
}/// Create a copy of Compatibilita
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CartaCopyWith<$Res> get cartaCoppia {
  
  return $CartaCopyWith<$Res>(_self.cartaCoppia, (value) {
    return _then(_self.copyWith(cartaCoppia: value));
  });
}/// Create a copy of Compatibilita
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CartaCopyWith<$Res> get cartaAnimaTu {
  
  return $CartaCopyWith<$Res>(_self.cartaAnimaTu, (value) {
    return _then(_self.copyWith(cartaAnimaTu: value));
  });
}/// Create a copy of Compatibilita
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CartaCopyWith<$Res> get cartaAnimaPartner {
  
  return $CartaCopyWith<$Res>(_self.cartaAnimaPartner, (value) {
    return _then(_self.copyWith(cartaAnimaPartner: value));
  });
}
}


/// Adds pattern-matching-related methods to [Compatibilita].
extension CompatibilitaPatterns on Compatibilita {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Compatibilita value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Compatibilita() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Compatibilita value)  $default,){
final _that = this;
switch (_that) {
case _Compatibilita():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Compatibilita value)?  $default,){
final _that = this;
switch (_that) {
case _Compatibilita() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( SegniCoppia segni,  int distanza,  String aspetto,  String relazioneElementi,  bool stessaModalita,  String armonia,  Carta cartaCoppia,  Carta cartaAnimaTu,  Carta cartaAnimaPartner)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Compatibilita() when $default != null:
return $default(_that.segni,_that.distanza,_that.aspetto,_that.relazioneElementi,_that.stessaModalita,_that.armonia,_that.cartaCoppia,_that.cartaAnimaTu,_that.cartaAnimaPartner);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( SegniCoppia segni,  int distanza,  String aspetto,  String relazioneElementi,  bool stessaModalita,  String armonia,  Carta cartaCoppia,  Carta cartaAnimaTu,  Carta cartaAnimaPartner)  $default,) {final _that = this;
switch (_that) {
case _Compatibilita():
return $default(_that.segni,_that.distanza,_that.aspetto,_that.relazioneElementi,_that.stessaModalita,_that.armonia,_that.cartaCoppia,_that.cartaAnimaTu,_that.cartaAnimaPartner);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( SegniCoppia segni,  int distanza,  String aspetto,  String relazioneElementi,  bool stessaModalita,  String armonia,  Carta cartaCoppia,  Carta cartaAnimaTu,  Carta cartaAnimaPartner)?  $default,) {final _that = this;
switch (_that) {
case _Compatibilita() when $default != null:
return $default(_that.segni,_that.distanza,_that.aspetto,_that.relazioneElementi,_that.stessaModalita,_that.armonia,_that.cartaCoppia,_that.cartaAnimaTu,_that.cartaAnimaPartner);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Compatibilita implements Compatibilita {
  const _Compatibilita({required this.segni, required this.distanza, required this.aspetto, required this.relazioneElementi, this.stessaModalita = false, required this.armonia, required this.cartaCoppia, required this.cartaAnimaTu, required this.cartaAnimaPartner});
  factory _Compatibilita.fromJson(Map<String, dynamic> json) => _$CompatibilitaFromJson(json);

@override final  SegniCoppia segni;
@override final  int distanza;
@override final  String aspetto;
@override final  String relazioneElementi;
@override@JsonKey() final  bool stessaModalita;
@override final  String armonia;
@override final  Carta cartaCoppia;
@override final  Carta cartaAnimaTu;
@override final  Carta cartaAnimaPartner;

/// Create a copy of Compatibilita
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CompatibilitaCopyWith<_Compatibilita> get copyWith => __$CompatibilitaCopyWithImpl<_Compatibilita>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CompatibilitaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Compatibilita&&(identical(other.segni, segni) || other.segni == segni)&&(identical(other.distanza, distanza) || other.distanza == distanza)&&(identical(other.aspetto, aspetto) || other.aspetto == aspetto)&&(identical(other.relazioneElementi, relazioneElementi) || other.relazioneElementi == relazioneElementi)&&(identical(other.stessaModalita, stessaModalita) || other.stessaModalita == stessaModalita)&&(identical(other.armonia, armonia) || other.armonia == armonia)&&(identical(other.cartaCoppia, cartaCoppia) || other.cartaCoppia == cartaCoppia)&&(identical(other.cartaAnimaTu, cartaAnimaTu) || other.cartaAnimaTu == cartaAnimaTu)&&(identical(other.cartaAnimaPartner, cartaAnimaPartner) || other.cartaAnimaPartner == cartaAnimaPartner));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,segni,distanza,aspetto,relazioneElementi,stessaModalita,armonia,cartaCoppia,cartaAnimaTu,cartaAnimaPartner);
}

@override
String toString() {
    return 'Compatibilita(segni: $segni, distanza: $distanza, aspetto: $aspetto, relazioneElementi: $relazioneElementi, stessaModalita: $stessaModalita, armonia: $armonia, cartaCoppia: $cartaCoppia, cartaAnimaTu: $cartaAnimaTu, cartaAnimaPartner: $cartaAnimaPartner)';
}


}

/// @nodoc
abstract mixin class _$CompatibilitaCopyWith<$Res> implements $CompatibilitaCopyWith<$Res> {
  factory _$CompatibilitaCopyWith(_Compatibilita value, $Res Function(_Compatibilita) _then) = __$CompatibilitaCopyWithImpl;
@override @useResult
$Res call({
 SegniCoppia segni, int distanza, String aspetto, String relazioneElementi, bool stessaModalita, String armonia, Carta cartaCoppia, Carta cartaAnimaTu, Carta cartaAnimaPartner
});


@override $SegniCoppiaCopyWith<$Res> get segni;@override $CartaCopyWith<$Res> get cartaCoppia;@override $CartaCopyWith<$Res> get cartaAnimaTu;@override $CartaCopyWith<$Res> get cartaAnimaPartner;

}
/// @nodoc
class __$CompatibilitaCopyWithImpl<$Res>
    implements _$CompatibilitaCopyWith<$Res> {
  __$CompatibilitaCopyWithImpl(this._self, this._then);

  final _Compatibilita _self;
  final $Res Function(_Compatibilita) _then;

/// Create a copy of Compatibilita
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? segni = null,Object? distanza = null,Object? aspetto = null,Object? relazioneElementi = null,Object? stessaModalita = null,Object? armonia = null,Object? cartaCoppia = null,Object? cartaAnimaTu = null,Object? cartaAnimaPartner = null,}) {
  return _then(_Compatibilita(
segni: null == segni ? _self.segni : segni // ignore: cast_nullable_to_non_nullable
as SegniCoppia,distanza: null == distanza ? _self.distanza : distanza // ignore: cast_nullable_to_non_nullable
as int,aspetto: null == aspetto ? _self.aspetto : aspetto // ignore: cast_nullable_to_non_nullable
as String,relazioneElementi: null == relazioneElementi ? _self.relazioneElementi : relazioneElementi // ignore: cast_nullable_to_non_nullable
as String,stessaModalita: null == stessaModalita ? _self.stessaModalita : stessaModalita // ignore: cast_nullable_to_non_nullable
as bool,armonia: null == armonia ? _self.armonia : armonia // ignore: cast_nullable_to_non_nullable
as String,cartaCoppia: null == cartaCoppia ? _self.cartaCoppia : cartaCoppia // ignore: cast_nullable_to_non_nullable
as Carta,cartaAnimaTu: null == cartaAnimaTu ? _self.cartaAnimaTu : cartaAnimaTu // ignore: cast_nullable_to_non_nullable
as Carta,cartaAnimaPartner: null == cartaAnimaPartner ? _self.cartaAnimaPartner : cartaAnimaPartner // ignore: cast_nullable_to_non_nullable
as Carta,
  ));
}

/// Create a copy of Compatibilita
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$SegniCoppiaCopyWith<$Res> get segni {
  
  return $SegniCoppiaCopyWith<$Res>(_self.segni, (value) {
    return _then(_self.copyWith(segni: value));
  });
}/// Create a copy of Compatibilita
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CartaCopyWith<$Res> get cartaCoppia {
  
  return $CartaCopyWith<$Res>(_self.cartaCoppia, (value) {
    return _then(_self.copyWith(cartaCoppia: value));
  });
}/// Create a copy of Compatibilita
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CartaCopyWith<$Res> get cartaAnimaTu {
  
  return $CartaCopyWith<$Res>(_self.cartaAnimaTu, (value) {
    return _then(_self.copyWith(cartaAnimaTu: value));
  });
}/// Create a copy of Compatibilita
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CartaCopyWith<$Res> get cartaAnimaPartner {
  
  return $CartaCopyWith<$Res>(_self.cartaAnimaPartner, (value) {
    return _then(_self.copyWith(cartaAnimaPartner: value));
  });
}
}


/// @nodoc
mixin _$Lettura {

 String get id;/// La cartella delle immagini del mazzo; `null` = il predefinito.
 String? get mazzo; String get spreadId; String get stesa; Map<String, String> get stesaNomi; String get categoria; String? get stile; PersoneLettura? get persone; Compatibilita? get compatibilita; String get question;/// `intervista`, `ventaglio`, `scelta`, `rivelazione`, `sintesi`, `completata`, `annullata`.
 String get status; String get lang; String get consumo; String get createdAt; String? get completedAt;/// `si`, `in_parte`, `no`.
 String? get feedback; bool get shared; bool get manuale; String? get contextSummary; List<TurnoIntervista> get interview; List<CartaPosata> get cards; int? get slotCount; List<int> get pickedSlots; String? get commitment; String? get deckSalt; String? get synthesis; String? get guardOutcome; String? get shareToken; String? get shareText; String? get feedbackNote; String get disclaimer; Map<String, Dignita> get dignita; Stesa? get stesaDati;
/// Create a copy of Lettura
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LetturaCopyWith<Lettura> get copyWith => _$LetturaCopyWithImpl<Lettura>(this as Lettura, _$identity);

  /// Serializes this Lettura to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Lettura;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Lettura&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.mazzo, _this.mazzo) || other.mazzo == _this.mazzo)&&(identical(other.spreadId, _this.spreadId) || other.spreadId == _this.spreadId)&&(identical(other.stesa, _this.stesa) || other.stesa == _this.stesa)&&const DeepCollectionEquality().equals(other.stesaNomi, _this.stesaNomi)&&(identical(other.categoria, _this.categoria) || other.categoria == _this.categoria)&&(identical(other.stile, _this.stile) || other.stile == _this.stile)&&(identical(other.persone, _this.persone) || other.persone == _this.persone)&&(identical(other.compatibilita, _this.compatibilita) || other.compatibilita == _this.compatibilita)&&(identical(other.question, _this.question) || other.question == _this.question)&&(identical(other.status, _this.status) || other.status == _this.status)&&(identical(other.lang, _this.lang) || other.lang == _this.lang)&&(identical(other.consumo, _this.consumo) || other.consumo == _this.consumo)&&(identical(other.createdAt, _this.createdAt) || other.createdAt == _this.createdAt)&&(identical(other.completedAt, _this.completedAt) || other.completedAt == _this.completedAt)&&(identical(other.feedback, _this.feedback) || other.feedback == _this.feedback)&&(identical(other.shared, _this.shared) || other.shared == _this.shared)&&(identical(other.manuale, _this.manuale) || other.manuale == _this.manuale)&&(identical(other.contextSummary, _this.contextSummary) || other.contextSummary == _this.contextSummary)&&const DeepCollectionEquality().equals(other.interview, _this.interview)&&const DeepCollectionEquality().equals(other.cards, _this.cards)&&(identical(other.slotCount, _this.slotCount) || other.slotCount == _this.slotCount)&&const DeepCollectionEquality().equals(other.pickedSlots, _this.pickedSlots)&&(identical(other.commitment, _this.commitment) || other.commitment == _this.commitment)&&(identical(other.deckSalt, _this.deckSalt) || other.deckSalt == _this.deckSalt)&&(identical(other.synthesis, _this.synthesis) || other.synthesis == _this.synthesis)&&(identical(other.guardOutcome, _this.guardOutcome) || other.guardOutcome == _this.guardOutcome)&&(identical(other.shareToken, _this.shareToken) || other.shareToken == _this.shareToken)&&(identical(other.shareText, _this.shareText) || other.shareText == _this.shareText)&&(identical(other.feedbackNote, _this.feedbackNote) || other.feedbackNote == _this.feedbackNote)&&(identical(other.disclaimer, _this.disclaimer) || other.disclaimer == _this.disclaimer)&&const DeepCollectionEquality().equals(other.dignita, _this.dignita)&&(identical(other.stesaDati, _this.stesaDati) || other.stesaDati == _this.stesaDati));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Lettura;
  return Object.hashAll([runtimeType,_this.id,_this.mazzo,_this.spreadId,_this.stesa,const DeepCollectionEquality().hash(_this.stesaNomi),_this.categoria,_this.stile,_this.persone,_this.compatibilita,_this.question,_this.status,_this.lang,_this.consumo,_this.createdAt,_this.completedAt,_this.feedback,_this.shared,_this.manuale,_this.contextSummary,const DeepCollectionEquality().hash(_this.interview),const DeepCollectionEquality().hash(_this.cards),_this.slotCount,const DeepCollectionEquality().hash(_this.pickedSlots),_this.commitment,_this.deckSalt,_this.synthesis,_this.guardOutcome,_this.shareToken,_this.shareText,_this.feedbackNote,_this.disclaimer,const DeepCollectionEquality().hash(_this.dignita),_this.stesaDati]);
}

@override
String toString() {
  final _this = this as Lettura;
  return 'Lettura(id: ${_this.id}, mazzo: ${_this.mazzo}, spreadId: ${_this.spreadId}, stesa: ${_this.stesa}, stesaNomi: ${_this.stesaNomi}, categoria: ${_this.categoria}, stile: ${_this.stile}, persone: ${_this.persone}, compatibilita: ${_this.compatibilita}, question: ${_this.question}, status: ${_this.status}, lang: ${_this.lang}, consumo: ${_this.consumo}, createdAt: ${_this.createdAt}, completedAt: ${_this.completedAt}, feedback: ${_this.feedback}, shared: ${_this.shared}, manuale: ${_this.manuale}, contextSummary: ${_this.contextSummary}, interview: ${_this.interview}, cards: ${_this.cards}, slotCount: ${_this.slotCount}, pickedSlots: ${_this.pickedSlots}, commitment: ${_this.commitment}, deckSalt: ${_this.deckSalt}, synthesis: ${_this.synthesis}, guardOutcome: ${_this.guardOutcome}, shareToken: ${_this.shareToken}, shareText: ${_this.shareText}, feedbackNote: ${_this.feedbackNote}, disclaimer: ${_this.disclaimer}, dignita: ${_this.dignita}, stesaDati: ${_this.stesaDati})';
}


}

/// @nodoc
abstract mixin class $LetturaCopyWith<$Res>  {
  factory $LetturaCopyWith(Lettura value, $Res Function(Lettura) _then) = _$LetturaCopyWithImpl;
@useResult
$Res call({
 String id, String? mazzo, String spreadId, String stesa, Map<String, String> stesaNomi, String categoria, String? stile, PersoneLettura? persone, Compatibilita? compatibilita, String question, String status, String lang, String consumo, String createdAt, String? completedAt, String? feedback, bool shared, bool manuale, String? contextSummary, List<TurnoIntervista> interview, List<CartaPosata> cards, int? slotCount, List<int> pickedSlots, String? commitment, String? deckSalt, String? synthesis, String? guardOutcome, String? shareToken, String? shareText, String? feedbackNote, String disclaimer, Map<String, Dignita> dignita, Stesa? stesaDati
});


$PersoneLetturaCopyWith<$Res>? get persone;$CompatibilitaCopyWith<$Res>? get compatibilita;$StesaCopyWith<$Res>? get stesaDati;

}
/// @nodoc
class _$LetturaCopyWithImpl<$Res>
    implements $LetturaCopyWith<$Res> {
  _$LetturaCopyWithImpl(this._self, this._then);

  final Lettura _self;
  final $Res Function(Lettura) _then;

/// Create a copy of Lettura
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? mazzo = freezed,Object? spreadId = null,Object? stesa = null,Object? stesaNomi = null,Object? categoria = null,Object? stile = freezed,Object? persone = freezed,Object? compatibilita = freezed,Object? question = null,Object? status = null,Object? lang = null,Object? consumo = null,Object? createdAt = null,Object? completedAt = freezed,Object? feedback = freezed,Object? shared = null,Object? manuale = null,Object? contextSummary = freezed,Object? interview = null,Object? cards = null,Object? slotCount = freezed,Object? pickedSlots = null,Object? commitment = freezed,Object? deckSalt = freezed,Object? synthesis = freezed,Object? guardOutcome = freezed,Object? shareToken = freezed,Object? shareText = freezed,Object? feedbackNote = freezed,Object? disclaimer = null,Object? dignita = null,Object? stesaDati = freezed,}) {
  return _then(Lettura(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,mazzo: freezed == mazzo ? _self.mazzo : mazzo // ignore: cast_nullable_to_non_nullable
as String?,spreadId: null == spreadId ? _self.spreadId : spreadId // ignore: cast_nullable_to_non_nullable
as String,stesa: null == stesa ? _self.stesa : stesa // ignore: cast_nullable_to_non_nullable
as String,stesaNomi: null == stesaNomi ? _self.stesaNomi : stesaNomi // ignore: cast_nullable_to_non_nullable
as Map<String, String>,categoria: null == categoria ? _self.categoria : categoria // ignore: cast_nullable_to_non_nullable
as String,stile: freezed == stile ? _self.stile : stile // ignore: cast_nullable_to_non_nullable
as String?,persone: freezed == persone ? _self.persone : persone // ignore: cast_nullable_to_non_nullable
as PersoneLettura?,compatibilita: freezed == compatibilita ? _self.compatibilita : compatibilita // ignore: cast_nullable_to_non_nullable
as Compatibilita?,question: null == question ? _self.question : question // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,lang: null == lang ? _self.lang : lang // ignore: cast_nullable_to_non_nullable
as String,consumo: null == consumo ? _self.consumo : consumo // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,completedAt: freezed == completedAt ? _self.completedAt : completedAt // ignore: cast_nullable_to_non_nullable
as String?,feedback: freezed == feedback ? _self.feedback : feedback // ignore: cast_nullable_to_non_nullable
as String?,shared: null == shared ? _self.shared : shared // ignore: cast_nullable_to_non_nullable
as bool,manuale: null == manuale ? _self.manuale : manuale // ignore: cast_nullable_to_non_nullable
as bool,contextSummary: freezed == contextSummary ? _self.contextSummary : contextSummary // ignore: cast_nullable_to_non_nullable
as String?,interview: null == interview ? _self.interview : interview // ignore: cast_nullable_to_non_nullable
as List<TurnoIntervista>,cards: null == cards ? _self.cards : cards // ignore: cast_nullable_to_non_nullable
as List<CartaPosata>,slotCount: freezed == slotCount ? _self.slotCount : slotCount // ignore: cast_nullable_to_non_nullable
as int?,pickedSlots: null == pickedSlots ? _self.pickedSlots : pickedSlots // ignore: cast_nullable_to_non_nullable
as List<int>,commitment: freezed == commitment ? _self.commitment : commitment // ignore: cast_nullable_to_non_nullable
as String?,deckSalt: freezed == deckSalt ? _self.deckSalt : deckSalt // ignore: cast_nullable_to_non_nullable
as String?,synthesis: freezed == synthesis ? _self.synthesis : synthesis // ignore: cast_nullable_to_non_nullable
as String?,guardOutcome: freezed == guardOutcome ? _self.guardOutcome : guardOutcome // ignore: cast_nullable_to_non_nullable
as String?,shareToken: freezed == shareToken ? _self.shareToken : shareToken // ignore: cast_nullable_to_non_nullable
as String?,shareText: freezed == shareText ? _self.shareText : shareText // ignore: cast_nullable_to_non_nullable
as String?,feedbackNote: freezed == feedbackNote ? _self.feedbackNote : feedbackNote // ignore: cast_nullable_to_non_nullable
as String?,disclaimer: null == disclaimer ? _self.disclaimer : disclaimer // ignore: cast_nullable_to_non_nullable
as String,dignita: null == dignita ? _self.dignita : dignita // ignore: cast_nullable_to_non_nullable
as Map<String, Dignita>,stesaDati: freezed == stesaDati ? _self.stesaDati : stesaDati // ignore: cast_nullable_to_non_nullable
as Stesa?,
  ));
}
/// Create a copy of Lettura
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PersoneLetturaCopyWith<$Res>? get persone {
    if (_self.persone == null) {
    return null;
  }

  return $PersoneLetturaCopyWith<$Res>(_self.persone!, (value) {
    return _then(_self.copyWith(persone: value));
  });
}/// Create a copy of Lettura
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CompatibilitaCopyWith<$Res>? get compatibilita {
    if (_self.compatibilita == null) {
    return null;
  }

  return $CompatibilitaCopyWith<$Res>(_self.compatibilita!, (value) {
    return _then(_self.copyWith(compatibilita: value));
  });
}/// Create a copy of Lettura
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$StesaCopyWith<$Res>? get stesaDati {
    if (_self.stesaDati == null) {
    return null;
  }

  return $StesaCopyWith<$Res>(_self.stesaDati!, (value) {
    return _then(_self.copyWith(stesaDati: value));
  });
}
}


/// Adds pattern-matching-related methods to [Lettura].
extension LetturaPatterns on Lettura {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Lettura value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Lettura() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Lettura value)  $default,){
final _that = this;
switch (_that) {
case _Lettura():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Lettura value)?  $default,){
final _that = this;
switch (_that) {
case _Lettura() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String? mazzo,  String spreadId,  String stesa,  Map<String, String> stesaNomi,  String categoria,  String? stile,  PersoneLettura? persone,  Compatibilita? compatibilita,  String question,  String status,  String lang,  String consumo,  String createdAt,  String? completedAt,  String? feedback,  bool shared,  bool manuale,  String? contextSummary,  List<TurnoIntervista> interview,  List<CartaPosata> cards,  int? slotCount,  List<int> pickedSlots,  String? commitment,  String? deckSalt,  String? synthesis,  String? guardOutcome,  String? shareToken,  String? shareText,  String? feedbackNote,  String disclaimer,  Map<String, Dignita> dignita,  Stesa? stesaDati)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Lettura() when $default != null:
return $default(_that.id,_that.mazzo,_that.spreadId,_that.stesa,_that.stesaNomi,_that.categoria,_that.stile,_that.persone,_that.compatibilita,_that.question,_that.status,_that.lang,_that.consumo,_that.createdAt,_that.completedAt,_that.feedback,_that.shared,_that.manuale,_that.contextSummary,_that.interview,_that.cards,_that.slotCount,_that.pickedSlots,_that.commitment,_that.deckSalt,_that.synthesis,_that.guardOutcome,_that.shareToken,_that.shareText,_that.feedbackNote,_that.disclaimer,_that.dignita,_that.stesaDati);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String? mazzo,  String spreadId,  String stesa,  Map<String, String> stesaNomi,  String categoria,  String? stile,  PersoneLettura? persone,  Compatibilita? compatibilita,  String question,  String status,  String lang,  String consumo,  String createdAt,  String? completedAt,  String? feedback,  bool shared,  bool manuale,  String? contextSummary,  List<TurnoIntervista> interview,  List<CartaPosata> cards,  int? slotCount,  List<int> pickedSlots,  String? commitment,  String? deckSalt,  String? synthesis,  String? guardOutcome,  String? shareToken,  String? shareText,  String? feedbackNote,  String disclaimer,  Map<String, Dignita> dignita,  Stesa? stesaDati)  $default,) {final _that = this;
switch (_that) {
case _Lettura():
return $default(_that.id,_that.mazzo,_that.spreadId,_that.stesa,_that.stesaNomi,_that.categoria,_that.stile,_that.persone,_that.compatibilita,_that.question,_that.status,_that.lang,_that.consumo,_that.createdAt,_that.completedAt,_that.feedback,_that.shared,_that.manuale,_that.contextSummary,_that.interview,_that.cards,_that.slotCount,_that.pickedSlots,_that.commitment,_that.deckSalt,_that.synthesis,_that.guardOutcome,_that.shareToken,_that.shareText,_that.feedbackNote,_that.disclaimer,_that.dignita,_that.stesaDati);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String? mazzo,  String spreadId,  String stesa,  Map<String, String> stesaNomi,  String categoria,  String? stile,  PersoneLettura? persone,  Compatibilita? compatibilita,  String question,  String status,  String lang,  String consumo,  String createdAt,  String? completedAt,  String? feedback,  bool shared,  bool manuale,  String? contextSummary,  List<TurnoIntervista> interview,  List<CartaPosata> cards,  int? slotCount,  List<int> pickedSlots,  String? commitment,  String? deckSalt,  String? synthesis,  String? guardOutcome,  String? shareToken,  String? shareText,  String? feedbackNote,  String disclaimer,  Map<String, Dignita> dignita,  Stesa? stesaDati)?  $default,) {final _that = this;
switch (_that) {
case _Lettura() when $default != null:
return $default(_that.id,_that.mazzo,_that.spreadId,_that.stesa,_that.stesaNomi,_that.categoria,_that.stile,_that.persone,_that.compatibilita,_that.question,_that.status,_that.lang,_that.consumo,_that.createdAt,_that.completedAt,_that.feedback,_that.shared,_that.manuale,_that.contextSummary,_that.interview,_that.cards,_that.slotCount,_that.pickedSlots,_that.commitment,_that.deckSalt,_that.synthesis,_that.guardOutcome,_that.shareToken,_that.shareText,_that.feedbackNote,_that.disclaimer,_that.dignita,_that.stesaDati);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Lettura implements Lettura {
  const _Lettura({required this.id, this.mazzo, required this.spreadId, required this.stesa,  Map<String, String> stesaNomi = const <String, String>{}, required this.categoria, this.stile, this.persone, this.compatibilita, required this.question, required this.status, required this.lang, this.consumo = '', required this.createdAt, this.completedAt, this.feedback, this.shared = false, this.manuale = false, this.contextSummary,  List<TurnoIntervista> interview = const <TurnoIntervista>[],  List<CartaPosata> cards = const <CartaPosata>[], this.slotCount,  List<int> pickedSlots = const <int>[], this.commitment, this.deckSalt, this.synthesis, this.guardOutcome, this.shareToken, this.shareText, this.feedbackNote, this.disclaimer = '',  Map<String, Dignita> dignita = const <String, Dignita>{}, this.stesaDati}): _stesaNomi = stesaNomi,_interview = interview,_cards = cards,_pickedSlots = pickedSlots,_dignita = dignita;
  factory _Lettura.fromJson(Map<String, dynamic> json) => _$LetturaFromJson(json);

@override final  String id;
/// La cartella delle immagini del mazzo; `null` = il predefinito.
@override final  String? mazzo;
@override final  String spreadId;
@override final  String stesa;
 final  Map<String, String> _stesaNomi;
@override@JsonKey() Map<String, String> get stesaNomi {
  if (_stesaNomi is EqualUnmodifiableMapView) return _stesaNomi;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_stesaNomi);
}

@override final  String categoria;
@override final  String? stile;
@override final  PersoneLettura? persone;
@override final  Compatibilita? compatibilita;
@override final  String question;
/// `intervista`, `ventaglio`, `scelta`, `rivelazione`, `sintesi`, `completata`, `annullata`.
@override final  String status;
@override final  String lang;
@override@JsonKey() final  String consumo;
@override final  String createdAt;
@override final  String? completedAt;
/// `si`, `in_parte`, `no`.
@override final  String? feedback;
@override@JsonKey() final  bool shared;
@override@JsonKey() final  bool manuale;
@override final  String? contextSummary;
 final  List<TurnoIntervista> _interview;
@override@JsonKey() List<TurnoIntervista> get interview {
  if (_interview is EqualUnmodifiableListView) return _interview;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_interview);
}

 final  List<CartaPosata> _cards;
@override@JsonKey() List<CartaPosata> get cards {
  if (_cards is EqualUnmodifiableListView) return _cards;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_cards);
}

@override final  int? slotCount;
 final  List<int> _pickedSlots;
@override@JsonKey() List<int> get pickedSlots {
  if (_pickedSlots is EqualUnmodifiableListView) return _pickedSlots;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_pickedSlots);
}

@override final  String? commitment;
@override final  String? deckSalt;
@override final  String? synthesis;
@override final  String? guardOutcome;
@override final  String? shareToken;
@override final  String? shareText;
@override final  String? feedbackNote;
@override@JsonKey() final  String disclaimer;
 final  Map<String, Dignita> _dignita;
@override@JsonKey() Map<String, Dignita> get dignita {
  if (_dignita is EqualUnmodifiableMapView) return _dignita;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_dignita);
}

@override final  Stesa? stesaDati;

/// Create a copy of Lettura
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$LetturaCopyWith<_Lettura> get copyWith => __$LetturaCopyWithImpl<_Lettura>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$LetturaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Lettura&&(identical(other.id, id) || other.id == id)&&(identical(other.mazzo, mazzo) || other.mazzo == mazzo)&&(identical(other.spreadId, spreadId) || other.spreadId == spreadId)&&(identical(other.stesa, stesa) || other.stesa == stesa)&&const DeepCollectionEquality().equals(other.stesaNomi, _stesaNomi)&&(identical(other.categoria, categoria) || other.categoria == categoria)&&(identical(other.stile, stile) || other.stile == stile)&&(identical(other.persone, persone) || other.persone == persone)&&(identical(other.compatibilita, compatibilita) || other.compatibilita == compatibilita)&&(identical(other.question, question) || other.question == question)&&(identical(other.status, status) || other.status == status)&&(identical(other.lang, lang) || other.lang == lang)&&(identical(other.consumo, consumo) || other.consumo == consumo)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.completedAt, completedAt) || other.completedAt == completedAt)&&(identical(other.feedback, feedback) || other.feedback == feedback)&&(identical(other.shared, shared) || other.shared == shared)&&(identical(other.manuale, manuale) || other.manuale == manuale)&&(identical(other.contextSummary, contextSummary) || other.contextSummary == contextSummary)&&const DeepCollectionEquality().equals(other.interview, _interview)&&const DeepCollectionEquality().equals(other.cards, _cards)&&(identical(other.slotCount, slotCount) || other.slotCount == slotCount)&&const DeepCollectionEquality().equals(other.pickedSlots, _pickedSlots)&&(identical(other.commitment, commitment) || other.commitment == commitment)&&(identical(other.deckSalt, deckSalt) || other.deckSalt == deckSalt)&&(identical(other.synthesis, synthesis) || other.synthesis == synthesis)&&(identical(other.guardOutcome, guardOutcome) || other.guardOutcome == guardOutcome)&&(identical(other.shareToken, shareToken) || other.shareToken == shareToken)&&(identical(other.shareText, shareText) || other.shareText == shareText)&&(identical(other.feedbackNote, feedbackNote) || other.feedbackNote == feedbackNote)&&(identical(other.disclaimer, disclaimer) || other.disclaimer == disclaimer)&&const DeepCollectionEquality().equals(other.dignita, _dignita)&&(identical(other.stesaDati, stesaDati) || other.stesaDati == stesaDati));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hashAll([runtimeType,id,mazzo,spreadId,stesa,const DeepCollectionEquality().hash(_stesaNomi),categoria,stile,persone,compatibilita,question,status,lang,consumo,createdAt,completedAt,feedback,shared,manuale,contextSummary,const DeepCollectionEquality().hash(_interview),const DeepCollectionEquality().hash(_cards),slotCount,const DeepCollectionEquality().hash(_pickedSlots),commitment,deckSalt,synthesis,guardOutcome,shareToken,shareText,feedbackNote,disclaimer,const DeepCollectionEquality().hash(_dignita),stesaDati]);
}

@override
String toString() {
    return 'Lettura(id: $id, mazzo: $mazzo, spreadId: $spreadId, stesa: $stesa, stesaNomi: $stesaNomi, categoria: $categoria, stile: $stile, persone: $persone, compatibilita: $compatibilita, question: $question, status: $status, lang: $lang, consumo: $consumo, createdAt: $createdAt, completedAt: $completedAt, feedback: $feedback, shared: $shared, manuale: $manuale, contextSummary: $contextSummary, interview: $interview, cards: $cards, slotCount: $slotCount, pickedSlots: $pickedSlots, commitment: $commitment, deckSalt: $deckSalt, synthesis: $synthesis, guardOutcome: $guardOutcome, shareToken: $shareToken, shareText: $shareText, feedbackNote: $feedbackNote, disclaimer: $disclaimer, dignita: $dignita, stesaDati: $stesaDati)';
}


}

/// @nodoc
abstract mixin class _$LetturaCopyWith<$Res> implements $LetturaCopyWith<$Res> {
  factory _$LetturaCopyWith(_Lettura value, $Res Function(_Lettura) _then) = __$LetturaCopyWithImpl;
@override @useResult
$Res call({
 String id, String? mazzo, String spreadId, String stesa, Map<String, String> stesaNomi, String categoria, String? stile, PersoneLettura? persone, Compatibilita? compatibilita, String question, String status, String lang, String consumo, String createdAt, String? completedAt, String? feedback, bool shared, bool manuale, String? contextSummary, List<TurnoIntervista> interview, List<CartaPosata> cards, int? slotCount, List<int> pickedSlots, String? commitment, String? deckSalt, String? synthesis, String? guardOutcome, String? shareToken, String? shareText, String? feedbackNote, String disclaimer, Map<String, Dignita> dignita, Stesa? stesaDati
});


@override $PersoneLetturaCopyWith<$Res>? get persone;@override $CompatibilitaCopyWith<$Res>? get compatibilita;@override $StesaCopyWith<$Res>? get stesaDati;

}
/// @nodoc
class __$LetturaCopyWithImpl<$Res>
    implements _$LetturaCopyWith<$Res> {
  __$LetturaCopyWithImpl(this._self, this._then);

  final _Lettura _self;
  final $Res Function(_Lettura) _then;

/// Create a copy of Lettura
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? mazzo = freezed,Object? spreadId = null,Object? stesa = null,Object? stesaNomi = null,Object? categoria = null,Object? stile = freezed,Object? persone = freezed,Object? compatibilita = freezed,Object? question = null,Object? status = null,Object? lang = null,Object? consumo = null,Object? createdAt = null,Object? completedAt = freezed,Object? feedback = freezed,Object? shared = null,Object? manuale = null,Object? contextSummary = freezed,Object? interview = null,Object? cards = null,Object? slotCount = freezed,Object? pickedSlots = null,Object? commitment = freezed,Object? deckSalt = freezed,Object? synthesis = freezed,Object? guardOutcome = freezed,Object? shareToken = freezed,Object? shareText = freezed,Object? feedbackNote = freezed,Object? disclaimer = null,Object? dignita = null,Object? stesaDati = freezed,}) {
  return _then(_Lettura(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,mazzo: freezed == mazzo ? _self.mazzo : mazzo // ignore: cast_nullable_to_non_nullable
as String?,spreadId: null == spreadId ? _self.spreadId : spreadId // ignore: cast_nullable_to_non_nullable
as String,stesa: null == stesa ? _self.stesa : stesa // ignore: cast_nullable_to_non_nullable
as String,stesaNomi: null == stesaNomi ? _self._stesaNomi : stesaNomi // ignore: cast_nullable_to_non_nullable
as Map<String, String>,categoria: null == categoria ? _self.categoria : categoria // ignore: cast_nullable_to_non_nullable
as String,stile: freezed == stile ? _self.stile : stile // ignore: cast_nullable_to_non_nullable
as String?,persone: freezed == persone ? _self.persone : persone // ignore: cast_nullable_to_non_nullable
as PersoneLettura?,compatibilita: freezed == compatibilita ? _self.compatibilita : compatibilita // ignore: cast_nullable_to_non_nullable
as Compatibilita?,question: null == question ? _self.question : question // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,lang: null == lang ? _self.lang : lang // ignore: cast_nullable_to_non_nullable
as String,consumo: null == consumo ? _self.consumo : consumo // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,completedAt: freezed == completedAt ? _self.completedAt : completedAt // ignore: cast_nullable_to_non_nullable
as String?,feedback: freezed == feedback ? _self.feedback : feedback // ignore: cast_nullable_to_non_nullable
as String?,shared: null == shared ? _self.shared : shared // ignore: cast_nullable_to_non_nullable
as bool,manuale: null == manuale ? _self.manuale : manuale // ignore: cast_nullable_to_non_nullable
as bool,contextSummary: freezed == contextSummary ? _self.contextSummary : contextSummary // ignore: cast_nullable_to_non_nullable
as String?,interview: null == interview ? _self._interview : interview // ignore: cast_nullable_to_non_nullable
as List<TurnoIntervista>,cards: null == cards ? _self._cards : cards // ignore: cast_nullable_to_non_nullable
as List<CartaPosata>,slotCount: freezed == slotCount ? _self.slotCount : slotCount // ignore: cast_nullable_to_non_nullable
as int?,pickedSlots: null == pickedSlots ? _self._pickedSlots : pickedSlots // ignore: cast_nullable_to_non_nullable
as List<int>,commitment: freezed == commitment ? _self.commitment : commitment // ignore: cast_nullable_to_non_nullable
as String?,deckSalt: freezed == deckSalt ? _self.deckSalt : deckSalt // ignore: cast_nullable_to_non_nullable
as String?,synthesis: freezed == synthesis ? _self.synthesis : synthesis // ignore: cast_nullable_to_non_nullable
as String?,guardOutcome: freezed == guardOutcome ? _self.guardOutcome : guardOutcome // ignore: cast_nullable_to_non_nullable
as String?,shareToken: freezed == shareToken ? _self.shareToken : shareToken // ignore: cast_nullable_to_non_nullable
as String?,shareText: freezed == shareText ? _self.shareText : shareText // ignore: cast_nullable_to_non_nullable
as String?,feedbackNote: freezed == feedbackNote ? _self.feedbackNote : feedbackNote // ignore: cast_nullable_to_non_nullable
as String?,disclaimer: null == disclaimer ? _self.disclaimer : disclaimer // ignore: cast_nullable_to_non_nullable
as String,dignita: null == dignita ? _self._dignita : dignita // ignore: cast_nullable_to_non_nullable
as Map<String, Dignita>,stesaDati: freezed == stesaDati ? _self.stesaDati : stesaDati // ignore: cast_nullable_to_non_nullable
as Stesa?,
  ));
}

/// Create a copy of Lettura
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PersoneLetturaCopyWith<$Res>? get persone {
    if (_self.persone == null) {
    return null;
  }

  return $PersoneLetturaCopyWith<$Res>(_self.persone!, (value) {
    return _then(_self.copyWith(persone: value));
  });
}/// Create a copy of Lettura
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CompatibilitaCopyWith<$Res>? get compatibilita {
    if (_self.compatibilita == null) {
    return null;
  }

  return $CompatibilitaCopyWith<$Res>(_self.compatibilita!, (value) {
    return _then(_self.copyWith(compatibilita: value));
  });
}/// Create a copy of Lettura
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$StesaCopyWith<$Res>? get stesaDati {
    if (_self.stesaDati == null) {
    return null;
  }

  return $StesaCopyWith<$Res>(_self.stesaDati!, (value) {
    return _then(_self.copyWith(stesaDati: value));
  });
}
}


/// @nodoc
mixin _$LetturaBreve {

 String get id; String? get mazzo; String get spreadId; String get stesa; Map<String, String> get stesaNomi; String get categoria; String? get stile; String? get partnerNome; String get question; String get status; String get createdAt; String? get completedAt; String? get feedback; bool get shared; List<String> get carte;
/// Create a copy of LetturaBreve
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LetturaBreveCopyWith<LetturaBreve> get copyWith => _$LetturaBreveCopyWithImpl<LetturaBreve>(this as LetturaBreve, _$identity);

  /// Serializes this LetturaBreve to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as LetturaBreve;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is LetturaBreve&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.mazzo, _this.mazzo) || other.mazzo == _this.mazzo)&&(identical(other.spreadId, _this.spreadId) || other.spreadId == _this.spreadId)&&(identical(other.stesa, _this.stesa) || other.stesa == _this.stesa)&&const DeepCollectionEquality().equals(other.stesaNomi, _this.stesaNomi)&&(identical(other.categoria, _this.categoria) || other.categoria == _this.categoria)&&(identical(other.stile, _this.stile) || other.stile == _this.stile)&&(identical(other.partnerNome, _this.partnerNome) || other.partnerNome == _this.partnerNome)&&(identical(other.question, _this.question) || other.question == _this.question)&&(identical(other.status, _this.status) || other.status == _this.status)&&(identical(other.createdAt, _this.createdAt) || other.createdAt == _this.createdAt)&&(identical(other.completedAt, _this.completedAt) || other.completedAt == _this.completedAt)&&(identical(other.feedback, _this.feedback) || other.feedback == _this.feedback)&&(identical(other.shared, _this.shared) || other.shared == _this.shared)&&const DeepCollectionEquality().equals(other.carte, _this.carte));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as LetturaBreve;
  return Object.hash(runtimeType,_this.id,_this.mazzo,_this.spreadId,_this.stesa,const DeepCollectionEquality().hash(_this.stesaNomi),_this.categoria,_this.stile,_this.partnerNome,_this.question,_this.status,_this.createdAt,_this.completedAt,_this.feedback,_this.shared,const DeepCollectionEquality().hash(_this.carte));
}

@override
String toString() {
  final _this = this as LetturaBreve;
  return 'LetturaBreve(id: ${_this.id}, mazzo: ${_this.mazzo}, spreadId: ${_this.spreadId}, stesa: ${_this.stesa}, stesaNomi: ${_this.stesaNomi}, categoria: ${_this.categoria}, stile: ${_this.stile}, partnerNome: ${_this.partnerNome}, question: ${_this.question}, status: ${_this.status}, createdAt: ${_this.createdAt}, completedAt: ${_this.completedAt}, feedback: ${_this.feedback}, shared: ${_this.shared}, carte: ${_this.carte})';
}


}

/// @nodoc
abstract mixin class $LetturaBreveCopyWith<$Res>  {
  factory $LetturaBreveCopyWith(LetturaBreve value, $Res Function(LetturaBreve) _then) = _$LetturaBreveCopyWithImpl;
@useResult
$Res call({
 String id, String? mazzo, String spreadId, String stesa, Map<String, String> stesaNomi, String categoria, String? stile, String? partnerNome, String question, String status, String createdAt, String? completedAt, String? feedback, bool shared, List<String> carte
});




}
/// @nodoc
class _$LetturaBreveCopyWithImpl<$Res>
    implements $LetturaBreveCopyWith<$Res> {
  _$LetturaBreveCopyWithImpl(this._self, this._then);

  final LetturaBreve _self;
  final $Res Function(LetturaBreve) _then;

/// Create a copy of LetturaBreve
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? mazzo = freezed,Object? spreadId = null,Object? stesa = null,Object? stesaNomi = null,Object? categoria = null,Object? stile = freezed,Object? partnerNome = freezed,Object? question = null,Object? status = null,Object? createdAt = null,Object? completedAt = freezed,Object? feedback = freezed,Object? shared = null,Object? carte = null,}) {
  return _then(LetturaBreve(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,mazzo: freezed == mazzo ? _self.mazzo : mazzo // ignore: cast_nullable_to_non_nullable
as String?,spreadId: null == spreadId ? _self.spreadId : spreadId // ignore: cast_nullable_to_non_nullable
as String,stesa: null == stesa ? _self.stesa : stesa // ignore: cast_nullable_to_non_nullable
as String,stesaNomi: null == stesaNomi ? _self.stesaNomi : stesaNomi // ignore: cast_nullable_to_non_nullable
as Map<String, String>,categoria: null == categoria ? _self.categoria : categoria // ignore: cast_nullable_to_non_nullable
as String,stile: freezed == stile ? _self.stile : stile // ignore: cast_nullable_to_non_nullable
as String?,partnerNome: freezed == partnerNome ? _self.partnerNome : partnerNome // ignore: cast_nullable_to_non_nullable
as String?,question: null == question ? _self.question : question // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,completedAt: freezed == completedAt ? _self.completedAt : completedAt // ignore: cast_nullable_to_non_nullable
as String?,feedback: freezed == feedback ? _self.feedback : feedback // ignore: cast_nullable_to_non_nullable
as String?,shared: null == shared ? _self.shared : shared // ignore: cast_nullable_to_non_nullable
as bool,carte: null == carte ? _self.carte : carte // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}

}


/// Adds pattern-matching-related methods to [LetturaBreve].
extension LetturaBrevePatterns on LetturaBreve {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _LetturaBreve value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _LetturaBreve() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _LetturaBreve value)  $default,){
final _that = this;
switch (_that) {
case _LetturaBreve():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _LetturaBreve value)?  $default,){
final _that = this;
switch (_that) {
case _LetturaBreve() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String? mazzo,  String spreadId,  String stesa,  Map<String, String> stesaNomi,  String categoria,  String? stile,  String? partnerNome,  String question,  String status,  String createdAt,  String? completedAt,  String? feedback,  bool shared,  List<String> carte)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _LetturaBreve() when $default != null:
return $default(_that.id,_that.mazzo,_that.spreadId,_that.stesa,_that.stesaNomi,_that.categoria,_that.stile,_that.partnerNome,_that.question,_that.status,_that.createdAt,_that.completedAt,_that.feedback,_that.shared,_that.carte);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String? mazzo,  String spreadId,  String stesa,  Map<String, String> stesaNomi,  String categoria,  String? stile,  String? partnerNome,  String question,  String status,  String createdAt,  String? completedAt,  String? feedback,  bool shared,  List<String> carte)  $default,) {final _that = this;
switch (_that) {
case _LetturaBreve():
return $default(_that.id,_that.mazzo,_that.spreadId,_that.stesa,_that.stesaNomi,_that.categoria,_that.stile,_that.partnerNome,_that.question,_that.status,_that.createdAt,_that.completedAt,_that.feedback,_that.shared,_that.carte);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String? mazzo,  String spreadId,  String stesa,  Map<String, String> stesaNomi,  String categoria,  String? stile,  String? partnerNome,  String question,  String status,  String createdAt,  String? completedAt,  String? feedback,  bool shared,  List<String> carte)?  $default,) {final _that = this;
switch (_that) {
case _LetturaBreve() when $default != null:
return $default(_that.id,_that.mazzo,_that.spreadId,_that.stesa,_that.stesaNomi,_that.categoria,_that.stile,_that.partnerNome,_that.question,_that.status,_that.createdAt,_that.completedAt,_that.feedback,_that.shared,_that.carte);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _LetturaBreve implements LetturaBreve {
  const _LetturaBreve({required this.id, this.mazzo, required this.spreadId, required this.stesa,  Map<String, String> stesaNomi = const <String, String>{}, required this.categoria, this.stile, this.partnerNome, required this.question, required this.status, required this.createdAt, this.completedAt, this.feedback, this.shared = false,  List<String> carte = const <String>[]}): _stesaNomi = stesaNomi,_carte = carte;
  factory _LetturaBreve.fromJson(Map<String, dynamic> json) => _$LetturaBreveFromJson(json);

@override final  String id;
@override final  String? mazzo;
@override final  String spreadId;
@override final  String stesa;
 final  Map<String, String> _stesaNomi;
@override@JsonKey() Map<String, String> get stesaNomi {
  if (_stesaNomi is EqualUnmodifiableMapView) return _stesaNomi;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_stesaNomi);
}

@override final  String categoria;
@override final  String? stile;
@override final  String? partnerNome;
@override final  String question;
@override final  String status;
@override final  String createdAt;
@override final  String? completedAt;
@override final  String? feedback;
@override@JsonKey() final  bool shared;
 final  List<String> _carte;
@override@JsonKey() List<String> get carte {
  if (_carte is EqualUnmodifiableListView) return _carte;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_carte);
}


/// Create a copy of LetturaBreve
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$LetturaBreveCopyWith<_LetturaBreve> get copyWith => __$LetturaBreveCopyWithImpl<_LetturaBreve>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$LetturaBreveToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _LetturaBreve&&(identical(other.id, id) || other.id == id)&&(identical(other.mazzo, mazzo) || other.mazzo == mazzo)&&(identical(other.spreadId, spreadId) || other.spreadId == spreadId)&&(identical(other.stesa, stesa) || other.stesa == stesa)&&const DeepCollectionEquality().equals(other.stesaNomi, _stesaNomi)&&(identical(other.categoria, categoria) || other.categoria == categoria)&&(identical(other.stile, stile) || other.stile == stile)&&(identical(other.partnerNome, partnerNome) || other.partnerNome == partnerNome)&&(identical(other.question, question) || other.question == question)&&(identical(other.status, status) || other.status == status)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.completedAt, completedAt) || other.completedAt == completedAt)&&(identical(other.feedback, feedback) || other.feedback == feedback)&&(identical(other.shared, shared) || other.shared == shared)&&const DeepCollectionEquality().equals(other.carte, _carte));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,mazzo,spreadId,stesa,const DeepCollectionEquality().hash(_stesaNomi),categoria,stile,partnerNome,question,status,createdAt,completedAt,feedback,shared,const DeepCollectionEquality().hash(_carte));
}

@override
String toString() {
    return 'LetturaBreve(id: $id, mazzo: $mazzo, spreadId: $spreadId, stesa: $stesa, stesaNomi: $stesaNomi, categoria: $categoria, stile: $stile, partnerNome: $partnerNome, question: $question, status: $status, createdAt: $createdAt, completedAt: $completedAt, feedback: $feedback, shared: $shared, carte: $carte)';
}


}

/// @nodoc
abstract mixin class _$LetturaBreveCopyWith<$Res> implements $LetturaBreveCopyWith<$Res> {
  factory _$LetturaBreveCopyWith(_LetturaBreve value, $Res Function(_LetturaBreve) _then) = __$LetturaBreveCopyWithImpl;
@override @useResult
$Res call({
 String id, String? mazzo, String spreadId, String stesa, Map<String, String> stesaNomi, String categoria, String? stile, String? partnerNome, String question, String status, String createdAt, String? completedAt, String? feedback, bool shared, List<String> carte
});




}
/// @nodoc
class __$LetturaBreveCopyWithImpl<$Res>
    implements _$LetturaBreveCopyWith<$Res> {
  __$LetturaBreveCopyWithImpl(this._self, this._then);

  final _LetturaBreve _self;
  final $Res Function(_LetturaBreve) _then;

/// Create a copy of LetturaBreve
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? mazzo = freezed,Object? spreadId = null,Object? stesa = null,Object? stesaNomi = null,Object? categoria = null,Object? stile = freezed,Object? partnerNome = freezed,Object? question = null,Object? status = null,Object? createdAt = null,Object? completedAt = freezed,Object? feedback = freezed,Object? shared = null,Object? carte = null,}) {
  return _then(_LetturaBreve(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,mazzo: freezed == mazzo ? _self.mazzo : mazzo // ignore: cast_nullable_to_non_nullable
as String?,spreadId: null == spreadId ? _self.spreadId : spreadId // ignore: cast_nullable_to_non_nullable
as String,stesa: null == stesa ? _self.stesa : stesa // ignore: cast_nullable_to_non_nullable
as String,stesaNomi: null == stesaNomi ? _self._stesaNomi : stesaNomi // ignore: cast_nullable_to_non_nullable
as Map<String, String>,categoria: null == categoria ? _self.categoria : categoria // ignore: cast_nullable_to_non_nullable
as String,stile: freezed == stile ? _self.stile : stile // ignore: cast_nullable_to_non_nullable
as String?,partnerNome: freezed == partnerNome ? _self.partnerNome : partnerNome // ignore: cast_nullable_to_non_nullable
as String?,question: null == question ? _self.question : question // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,completedAt: freezed == completedAt ? _self.completedAt : completedAt // ignore: cast_nullable_to_non_nullable
as String?,feedback: freezed == feedback ? _self.feedback : feedback // ignore: cast_nullable_to_non_nullable
as String?,shared: null == shared ? _self.shared : shared // ignore: cast_nullable_to_non_nullable
as bool,carte: null == carte ? _self._carte : carte // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}


}


/// @nodoc
mixin _$ElencoLetture {

 int get totale; List<LetturaBreve> get letture;
/// Create a copy of ElencoLetture
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ElencoLettureCopyWith<ElencoLetture> get copyWith => _$ElencoLettureCopyWithImpl<ElencoLetture>(this as ElencoLetture, _$identity);

  /// Serializes this ElencoLetture to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as ElencoLetture;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ElencoLetture&&(identical(other.totale, _this.totale) || other.totale == _this.totale)&&const DeepCollectionEquality().equals(other.letture, _this.letture));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as ElencoLetture;
  return Object.hash(runtimeType,_this.totale,const DeepCollectionEquality().hash(_this.letture));
}

@override
String toString() {
  final _this = this as ElencoLetture;
  return 'ElencoLetture(totale: ${_this.totale}, letture: ${_this.letture})';
}


}

/// @nodoc
abstract mixin class $ElencoLettureCopyWith<$Res>  {
  factory $ElencoLettureCopyWith(ElencoLetture value, $Res Function(ElencoLetture) _then) = _$ElencoLettureCopyWithImpl;
@useResult
$Res call({
 int totale, List<LetturaBreve> letture
});




}
/// @nodoc
class _$ElencoLettureCopyWithImpl<$Res>
    implements $ElencoLettureCopyWith<$Res> {
  _$ElencoLettureCopyWithImpl(this._self, this._then);

  final ElencoLetture _self;
  final $Res Function(ElencoLetture) _then;

/// Create a copy of ElencoLetture
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? totale = null,Object? letture = null,}) {
  return _then(ElencoLetture(
totale: null == totale ? _self.totale : totale // ignore: cast_nullable_to_non_nullable
as int,letture: null == letture ? _self.letture : letture // ignore: cast_nullable_to_non_nullable
as List<LetturaBreve>,
  ));
}

}


/// Adds pattern-matching-related methods to [ElencoLetture].
extension ElencoLetturePatterns on ElencoLetture {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ElencoLetture value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ElencoLetture() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ElencoLetture value)  $default,){
final _that = this;
switch (_that) {
case _ElencoLetture():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ElencoLetture value)?  $default,){
final _that = this;
switch (_that) {
case _ElencoLetture() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int totale,  List<LetturaBreve> letture)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ElencoLetture() when $default != null:
return $default(_that.totale,_that.letture);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int totale,  List<LetturaBreve> letture)  $default,) {final _that = this;
switch (_that) {
case _ElencoLetture():
return $default(_that.totale,_that.letture);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int totale,  List<LetturaBreve> letture)?  $default,) {final _that = this;
switch (_that) {
case _ElencoLetture() when $default != null:
return $default(_that.totale,_that.letture);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ElencoLetture implements ElencoLetture {
  const _ElencoLetture({required this.totale,  List<LetturaBreve> letture = const <LetturaBreve>[]}): _letture = letture;
  factory _ElencoLetture.fromJson(Map<String, dynamic> json) => _$ElencoLettureFromJson(json);

@override final  int totale;
 final  List<LetturaBreve> _letture;
@override@JsonKey() List<LetturaBreve> get letture {
  if (_letture is EqualUnmodifiableListView) return _letture;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_letture);
}


/// Create a copy of ElencoLetture
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ElencoLettureCopyWith<_ElencoLetture> get copyWith => __$ElencoLettureCopyWithImpl<_ElencoLetture>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ElencoLettureToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _ElencoLetture&&(identical(other.totale, totale) || other.totale == totale)&&const DeepCollectionEquality().equals(other.letture, _letture));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,totale,const DeepCollectionEquality().hash(_letture));
}

@override
String toString() {
    return 'ElencoLetture(totale: $totale, letture: $letture)';
}


}

/// @nodoc
abstract mixin class _$ElencoLettureCopyWith<$Res> implements $ElencoLettureCopyWith<$Res> {
  factory _$ElencoLettureCopyWith(_ElencoLetture value, $Res Function(_ElencoLetture) _then) = __$ElencoLettureCopyWithImpl;
@override @useResult
$Res call({
 int totale, List<LetturaBreve> letture
});




}
/// @nodoc
class __$ElencoLettureCopyWithImpl<$Res>
    implements _$ElencoLettureCopyWith<$Res> {
  __$ElencoLettureCopyWithImpl(this._self, this._then);

  final _ElencoLetture _self;
  final $Res Function(_ElencoLetture) _then;

/// Create a copy of ElencoLetture
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? totale = null,Object? letture = null,}) {
  return _then(_ElencoLetture(
totale: null == totale ? _self.totale : totale // ignore: cast_nullable_to_non_nullable
as int,letture: null == letture ? _self._letture : letture // ignore: cast_nullable_to_non_nullable
as List<LetturaBreve>,
  ));
}


}


/// @nodoc
mixin _$Apertura {

 String? get id; String? get status; String? get categoria;/// La lingua del quesito, ricavata dal server: quella di domande e responso.
 String? get lang; String? get consumo; String? get disclaimer; Stesa? get stesa; int? get saldo; bool get crisi; String? get messaggio;
/// Create a copy of Apertura
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AperturaCopyWith<Apertura> get copyWith => _$AperturaCopyWithImpl<Apertura>(this as Apertura, _$identity);

  /// Serializes this Apertura to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Apertura;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Apertura&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.status, _this.status) || other.status == _this.status)&&(identical(other.categoria, _this.categoria) || other.categoria == _this.categoria)&&(identical(other.lang, _this.lang) || other.lang == _this.lang)&&(identical(other.consumo, _this.consumo) || other.consumo == _this.consumo)&&(identical(other.disclaimer, _this.disclaimer) || other.disclaimer == _this.disclaimer)&&(identical(other.stesa, _this.stesa) || other.stesa == _this.stesa)&&(identical(other.saldo, _this.saldo) || other.saldo == _this.saldo)&&(identical(other.crisi, _this.crisi) || other.crisi == _this.crisi)&&(identical(other.messaggio, _this.messaggio) || other.messaggio == _this.messaggio));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Apertura;
  return Object.hash(runtimeType,_this.id,_this.status,_this.categoria,_this.lang,_this.consumo,_this.disclaimer,_this.stesa,_this.saldo,_this.crisi,_this.messaggio);
}

@override
String toString() {
  final _this = this as Apertura;
  return 'Apertura(id: ${_this.id}, status: ${_this.status}, categoria: ${_this.categoria}, lang: ${_this.lang}, consumo: ${_this.consumo}, disclaimer: ${_this.disclaimer}, stesa: ${_this.stesa}, saldo: ${_this.saldo}, crisi: ${_this.crisi}, messaggio: ${_this.messaggio})';
}


}

/// @nodoc
abstract mixin class $AperturaCopyWith<$Res>  {
  factory $AperturaCopyWith(Apertura value, $Res Function(Apertura) _then) = _$AperturaCopyWithImpl;
@useResult
$Res call({
 String? id, String? status, String? categoria, String? lang, String? consumo, String? disclaimer, Stesa? stesa, int? saldo, bool crisi, String? messaggio
});


$StesaCopyWith<$Res>? get stesa;

}
/// @nodoc
class _$AperturaCopyWithImpl<$Res>
    implements $AperturaCopyWith<$Res> {
  _$AperturaCopyWithImpl(this._self, this._then);

  final Apertura _self;
  final $Res Function(Apertura) _then;

/// Create a copy of Apertura
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = freezed,Object? status = freezed,Object? categoria = freezed,Object? lang = freezed,Object? consumo = freezed,Object? disclaimer = freezed,Object? stesa = freezed,Object? saldo = freezed,Object? crisi = null,Object? messaggio = freezed,}) {
  return _then(Apertura(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,status: freezed == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String?,categoria: freezed == categoria ? _self.categoria : categoria // ignore: cast_nullable_to_non_nullable
as String?,lang: freezed == lang ? _self.lang : lang // ignore: cast_nullable_to_non_nullable
as String?,consumo: freezed == consumo ? _self.consumo : consumo // ignore: cast_nullable_to_non_nullable
as String?,disclaimer: freezed == disclaimer ? _self.disclaimer : disclaimer // ignore: cast_nullable_to_non_nullable
as String?,stesa: freezed == stesa ? _self.stesa : stesa // ignore: cast_nullable_to_non_nullable
as Stesa?,saldo: freezed == saldo ? _self.saldo : saldo // ignore: cast_nullable_to_non_nullable
as int?,crisi: null == crisi ? _self.crisi : crisi // ignore: cast_nullable_to_non_nullable
as bool,messaggio: freezed == messaggio ? _self.messaggio : messaggio // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}
/// Create a copy of Apertura
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$StesaCopyWith<$Res>? get stesa {
    if (_self.stesa == null) {
    return null;
  }

  return $StesaCopyWith<$Res>(_self.stesa!, (value) {
    return _then(_self.copyWith(stesa: value));
  });
}
}


/// Adds pattern-matching-related methods to [Apertura].
extension AperturaPatterns on Apertura {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Apertura value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Apertura() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Apertura value)  $default,){
final _that = this;
switch (_that) {
case _Apertura():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Apertura value)?  $default,){
final _that = this;
switch (_that) {
case _Apertura() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? id,  String? status,  String? categoria,  String? lang,  String? consumo,  String? disclaimer,  Stesa? stesa,  int? saldo,  bool crisi,  String? messaggio)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Apertura() when $default != null:
return $default(_that.id,_that.status,_that.categoria,_that.lang,_that.consumo,_that.disclaimer,_that.stesa,_that.saldo,_that.crisi,_that.messaggio);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? id,  String? status,  String? categoria,  String? lang,  String? consumo,  String? disclaimer,  Stesa? stesa,  int? saldo,  bool crisi,  String? messaggio)  $default,) {final _that = this;
switch (_that) {
case _Apertura():
return $default(_that.id,_that.status,_that.categoria,_that.lang,_that.consumo,_that.disclaimer,_that.stesa,_that.saldo,_that.crisi,_that.messaggio);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? id,  String? status,  String? categoria,  String? lang,  String? consumo,  String? disclaimer,  Stesa? stesa,  int? saldo,  bool crisi,  String? messaggio)?  $default,) {final _that = this;
switch (_that) {
case _Apertura() when $default != null:
return $default(_that.id,_that.status,_that.categoria,_that.lang,_that.consumo,_that.disclaimer,_that.stesa,_that.saldo,_that.crisi,_that.messaggio);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Apertura implements Apertura {
  const _Apertura({this.id, this.status, this.categoria, this.lang, this.consumo, this.disclaimer, this.stesa, this.saldo, this.crisi = false, this.messaggio});
  factory _Apertura.fromJson(Map<String, dynamic> json) => _$AperturaFromJson(json);

@override final  String? id;
@override final  String? status;
@override final  String? categoria;
/// La lingua del quesito, ricavata dal server: quella di domande e responso.
@override final  String? lang;
@override final  String? consumo;
@override final  String? disclaimer;
@override final  Stesa? stesa;
@override final  int? saldo;
@override@JsonKey() final  bool crisi;
@override final  String? messaggio;

/// Create a copy of Apertura
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$AperturaCopyWith<_Apertura> get copyWith => __$AperturaCopyWithImpl<_Apertura>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$AperturaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Apertura&&(identical(other.id, id) || other.id == id)&&(identical(other.status, status) || other.status == status)&&(identical(other.categoria, categoria) || other.categoria == categoria)&&(identical(other.lang, lang) || other.lang == lang)&&(identical(other.consumo, consumo) || other.consumo == consumo)&&(identical(other.disclaimer, disclaimer) || other.disclaimer == disclaimer)&&(identical(other.stesa, stesa) || other.stesa == stesa)&&(identical(other.saldo, saldo) || other.saldo == saldo)&&(identical(other.crisi, crisi) || other.crisi == crisi)&&(identical(other.messaggio, messaggio) || other.messaggio == messaggio));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,status,categoria,lang,consumo,disclaimer,stesa,saldo,crisi,messaggio);
}

@override
String toString() {
    return 'Apertura(id: $id, status: $status, categoria: $categoria, lang: $lang, consumo: $consumo, disclaimer: $disclaimer, stesa: $stesa, saldo: $saldo, crisi: $crisi, messaggio: $messaggio)';
}


}

/// @nodoc
abstract mixin class _$AperturaCopyWith<$Res> implements $AperturaCopyWith<$Res> {
  factory _$AperturaCopyWith(_Apertura value, $Res Function(_Apertura) _then) = __$AperturaCopyWithImpl;
@override @useResult
$Res call({
 String? id, String? status, String? categoria, String? lang, String? consumo, String? disclaimer, Stesa? stesa, int? saldo, bool crisi, String? messaggio
});


@override $StesaCopyWith<$Res>? get stesa;

}
/// @nodoc
class __$AperturaCopyWithImpl<$Res>
    implements _$AperturaCopyWith<$Res> {
  __$AperturaCopyWithImpl(this._self, this._then);

  final _Apertura _self;
  final $Res Function(_Apertura) _then;

/// Create a copy of Apertura
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? status = freezed,Object? categoria = freezed,Object? lang = freezed,Object? consumo = freezed,Object? disclaimer = freezed,Object? stesa = freezed,Object? saldo = freezed,Object? crisi = null,Object? messaggio = freezed,}) {
  return _then(_Apertura(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,status: freezed == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String?,categoria: freezed == categoria ? _self.categoria : categoria // ignore: cast_nullable_to_non_nullable
as String?,lang: freezed == lang ? _self.lang : lang // ignore: cast_nullable_to_non_nullable
as String?,consumo: freezed == consumo ? _self.consumo : consumo // ignore: cast_nullable_to_non_nullable
as String?,disclaimer: freezed == disclaimer ? _self.disclaimer : disclaimer // ignore: cast_nullable_to_non_nullable
as String?,stesa: freezed == stesa ? _self.stesa : stesa // ignore: cast_nullable_to_non_nullable
as Stesa?,saldo: freezed == saldo ? _self.saldo : saldo // ignore: cast_nullable_to_non_nullable
as int?,crisi: null == crisi ? _self.crisi : crisi // ignore: cast_nullable_to_non_nullable
as bool,messaggio: freezed == messaggio ? _self.messaggio : messaggio // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of Apertura
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$StesaCopyWith<$Res>? get stesa {
    if (_self.stesa == null) {
    return null;
  }

  return $StesaCopyWith<$Res>(_self.stesa!, (value) {
    return _then(_self.copyWith(stesa: value));
  });
}
}


/// @nodoc
mixin _$PassoIntervista {

 bool get completa; String? get domanda; int? get ordine; String? get riassunto; bool get crisi; String? get messaggio;/// Il minimo di domande è raggiunto: ci si può fermare («Basta con le domande»).
 bool get facoltativa;/// v9.5: dopo una risposta il server non chiede subito un'altra domanda: tocca a chi legge scegliere (i tre
/// pulsanti).
 bool get scelta;/// v9.5: le domande poste finora, e il minimo e il massimo della console.
 int? get poste; int? get minDomande; int? get maxDomande;
/// Create a copy of PassoIntervista
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PassoIntervistaCopyWith<PassoIntervista> get copyWith => _$PassoIntervistaCopyWithImpl<PassoIntervista>(this as PassoIntervista, _$identity);

  /// Serializes this PassoIntervista to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as PassoIntervista;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PassoIntervista&&(identical(other.completa, _this.completa) || other.completa == _this.completa)&&(identical(other.domanda, _this.domanda) || other.domanda == _this.domanda)&&(identical(other.ordine, _this.ordine) || other.ordine == _this.ordine)&&(identical(other.riassunto, _this.riassunto) || other.riassunto == _this.riassunto)&&(identical(other.crisi, _this.crisi) || other.crisi == _this.crisi)&&(identical(other.messaggio, _this.messaggio) || other.messaggio == _this.messaggio)&&(identical(other.facoltativa, _this.facoltativa) || other.facoltativa == _this.facoltativa)&&(identical(other.scelta, _this.scelta) || other.scelta == _this.scelta)&&(identical(other.poste, _this.poste) || other.poste == _this.poste)&&(identical(other.minDomande, _this.minDomande) || other.minDomande == _this.minDomande)&&(identical(other.maxDomande, _this.maxDomande) || other.maxDomande == _this.maxDomande));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as PassoIntervista;
  return Object.hash(runtimeType,_this.completa,_this.domanda,_this.ordine,_this.riassunto,_this.crisi,_this.messaggio,_this.facoltativa,_this.scelta,_this.poste,_this.minDomande,_this.maxDomande);
}

@override
String toString() {
  final _this = this as PassoIntervista;
  return 'PassoIntervista(completa: ${_this.completa}, domanda: ${_this.domanda}, ordine: ${_this.ordine}, riassunto: ${_this.riassunto}, crisi: ${_this.crisi}, messaggio: ${_this.messaggio}, facoltativa: ${_this.facoltativa}, scelta: ${_this.scelta}, poste: ${_this.poste}, minDomande: ${_this.minDomande}, maxDomande: ${_this.maxDomande})';
}


}

/// @nodoc
abstract mixin class $PassoIntervistaCopyWith<$Res>  {
  factory $PassoIntervistaCopyWith(PassoIntervista value, $Res Function(PassoIntervista) _then) = _$PassoIntervistaCopyWithImpl;
@useResult
$Res call({
 bool completa, String? domanda, int? ordine, String? riassunto, bool crisi, String? messaggio, bool facoltativa, bool scelta, int? poste, int? minDomande, int? maxDomande
});




}
/// @nodoc
class _$PassoIntervistaCopyWithImpl<$Res>
    implements $PassoIntervistaCopyWith<$Res> {
  _$PassoIntervistaCopyWithImpl(this._self, this._then);

  final PassoIntervista _self;
  final $Res Function(PassoIntervista) _then;

/// Create a copy of PassoIntervista
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? completa = null,Object? domanda = freezed,Object? ordine = freezed,Object? riassunto = freezed,Object? crisi = null,Object? messaggio = freezed,Object? facoltativa = null,Object? scelta = null,Object? poste = freezed,Object? minDomande = freezed,Object? maxDomande = freezed,}) {
  return _then(PassoIntervista(
completa: null == completa ? _self.completa : completa // ignore: cast_nullable_to_non_nullable
as bool,domanda: freezed == domanda ? _self.domanda : domanda // ignore: cast_nullable_to_non_nullable
as String?,ordine: freezed == ordine ? _self.ordine : ordine // ignore: cast_nullable_to_non_nullable
as int?,riassunto: freezed == riassunto ? _self.riassunto : riassunto // ignore: cast_nullable_to_non_nullable
as String?,crisi: null == crisi ? _self.crisi : crisi // ignore: cast_nullable_to_non_nullable
as bool,messaggio: freezed == messaggio ? _self.messaggio : messaggio // ignore: cast_nullable_to_non_nullable
as String?,facoltativa: null == facoltativa ? _self.facoltativa : facoltativa // ignore: cast_nullable_to_non_nullable
as bool,scelta: null == scelta ? _self.scelta : scelta // ignore: cast_nullable_to_non_nullable
as bool,poste: freezed == poste ? _self.poste : poste // ignore: cast_nullable_to_non_nullable
as int?,minDomande: freezed == minDomande ? _self.minDomande : minDomande // ignore: cast_nullable_to_non_nullable
as int?,maxDomande: freezed == maxDomande ? _self.maxDomande : maxDomande // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}

}


/// Adds pattern-matching-related methods to [PassoIntervista].
extension PassoIntervistaPatterns on PassoIntervista {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PassoIntervista value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PassoIntervista() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PassoIntervista value)  $default,){
final _that = this;
switch (_that) {
case _PassoIntervista():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PassoIntervista value)?  $default,){
final _that = this;
switch (_that) {
case _PassoIntervista() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( bool completa,  String? domanda,  int? ordine,  String? riassunto,  bool crisi,  String? messaggio,  bool facoltativa,  bool scelta,  int? poste,  int? minDomande,  int? maxDomande)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PassoIntervista() when $default != null:
return $default(_that.completa,_that.domanda,_that.ordine,_that.riassunto,_that.crisi,_that.messaggio,_that.facoltativa,_that.scelta,_that.poste,_that.minDomande,_that.maxDomande);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( bool completa,  String? domanda,  int? ordine,  String? riassunto,  bool crisi,  String? messaggio,  bool facoltativa,  bool scelta,  int? poste,  int? minDomande,  int? maxDomande)  $default,) {final _that = this;
switch (_that) {
case _PassoIntervista():
return $default(_that.completa,_that.domanda,_that.ordine,_that.riassunto,_that.crisi,_that.messaggio,_that.facoltativa,_that.scelta,_that.poste,_that.minDomande,_that.maxDomande);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( bool completa,  String? domanda,  int? ordine,  String? riassunto,  bool crisi,  String? messaggio,  bool facoltativa,  bool scelta,  int? poste,  int? minDomande,  int? maxDomande)?  $default,) {final _that = this;
switch (_that) {
case _PassoIntervista() when $default != null:
return $default(_that.completa,_that.domanda,_that.ordine,_that.riassunto,_that.crisi,_that.messaggio,_that.facoltativa,_that.scelta,_that.poste,_that.minDomande,_that.maxDomande);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _PassoIntervista implements PassoIntervista {
  const _PassoIntervista({this.completa = false, this.domanda, this.ordine, this.riassunto, this.crisi = false, this.messaggio, this.facoltativa = false, this.scelta = false, this.poste, this.minDomande, this.maxDomande});
  factory _PassoIntervista.fromJson(Map<String, dynamic> json) => _$PassoIntervistaFromJson(json);

@override@JsonKey() final  bool completa;
@override final  String? domanda;
@override final  int? ordine;
@override final  String? riassunto;
@override@JsonKey() final  bool crisi;
@override final  String? messaggio;
/// Il minimo di domande è raggiunto: ci si può fermare («Basta con le domande»).
@override@JsonKey() final  bool facoltativa;
/// v9.5: dopo una risposta il server non chiede subito un'altra domanda: tocca a chi legge scegliere (i tre
/// pulsanti).
@override@JsonKey() final  bool scelta;
/// v9.5: le domande poste finora, e il minimo e il massimo della console.
@override final  int? poste;
@override final  int? minDomande;
@override final  int? maxDomande;

/// Create a copy of PassoIntervista
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PassoIntervistaCopyWith<_PassoIntervista> get copyWith => __$PassoIntervistaCopyWithImpl<_PassoIntervista>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PassoIntervistaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _PassoIntervista&&(identical(other.completa, completa) || other.completa == completa)&&(identical(other.domanda, domanda) || other.domanda == domanda)&&(identical(other.ordine, ordine) || other.ordine == ordine)&&(identical(other.riassunto, riassunto) || other.riassunto == riassunto)&&(identical(other.crisi, crisi) || other.crisi == crisi)&&(identical(other.messaggio, messaggio) || other.messaggio == messaggio)&&(identical(other.facoltativa, facoltativa) || other.facoltativa == facoltativa)&&(identical(other.scelta, scelta) || other.scelta == scelta)&&(identical(other.poste, poste) || other.poste == poste)&&(identical(other.minDomande, minDomande) || other.minDomande == minDomande)&&(identical(other.maxDomande, maxDomande) || other.maxDomande == maxDomande));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,completa,domanda,ordine,riassunto,crisi,messaggio,facoltativa,scelta,poste,minDomande,maxDomande);
}

@override
String toString() {
    return 'PassoIntervista(completa: $completa, domanda: $domanda, ordine: $ordine, riassunto: $riassunto, crisi: $crisi, messaggio: $messaggio, facoltativa: $facoltativa, scelta: $scelta, poste: $poste, minDomande: $minDomande, maxDomande: $maxDomande)';
}


}

/// @nodoc
abstract mixin class _$PassoIntervistaCopyWith<$Res> implements $PassoIntervistaCopyWith<$Res> {
  factory _$PassoIntervistaCopyWith(_PassoIntervista value, $Res Function(_PassoIntervista) _then) = __$PassoIntervistaCopyWithImpl;
@override @useResult
$Res call({
 bool completa, String? domanda, int? ordine, String? riassunto, bool crisi, String? messaggio, bool facoltativa, bool scelta, int? poste, int? minDomande, int? maxDomande
});




}
/// @nodoc
class __$PassoIntervistaCopyWithImpl<$Res>
    implements _$PassoIntervistaCopyWith<$Res> {
  __$PassoIntervistaCopyWithImpl(this._self, this._then);

  final _PassoIntervista _self;
  final $Res Function(_PassoIntervista) _then;

/// Create a copy of PassoIntervista
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? completa = null,Object? domanda = freezed,Object? ordine = freezed,Object? riassunto = freezed,Object? crisi = null,Object? messaggio = freezed,Object? facoltativa = null,Object? scelta = null,Object? poste = freezed,Object? minDomande = freezed,Object? maxDomande = freezed,}) {
  return _then(_PassoIntervista(
completa: null == completa ? _self.completa : completa // ignore: cast_nullable_to_non_nullable
as bool,domanda: freezed == domanda ? _self.domanda : domanda // ignore: cast_nullable_to_non_nullable
as String?,ordine: freezed == ordine ? _self.ordine : ordine // ignore: cast_nullable_to_non_nullable
as int?,riassunto: freezed == riassunto ? _self.riassunto : riassunto // ignore: cast_nullable_to_non_nullable
as String?,crisi: null == crisi ? _self.crisi : crisi // ignore: cast_nullable_to_non_nullable
as bool,messaggio: freezed == messaggio ? _self.messaggio : messaggio // ignore: cast_nullable_to_non_nullable
as String?,facoltativa: null == facoltativa ? _self.facoltativa : facoltativa // ignore: cast_nullable_to_non_nullable
as bool,scelta: null == scelta ? _self.scelta : scelta // ignore: cast_nullable_to_non_nullable
as bool,poste: freezed == poste ? _self.poste : poste // ignore: cast_nullable_to_non_nullable
as int?,minDomande: freezed == minDomande ? _self.minDomande : minDomande // ignore: cast_nullable_to_non_nullable
as int?,maxDomande: freezed == maxDomande ? _self.maxDomande : maxDomande // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}


}


/// @nodoc
mixin _$Ventaglio {

 int get slotCount; String get commitment; int get daScegliere; List<int> get pickedSlots;
/// Create a copy of Ventaglio
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$VentaglioCopyWith<Ventaglio> get copyWith => _$VentaglioCopyWithImpl<Ventaglio>(this as Ventaglio, _$identity);

  /// Serializes this Ventaglio to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Ventaglio;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Ventaglio&&(identical(other.slotCount, _this.slotCount) || other.slotCount == _this.slotCount)&&(identical(other.commitment, _this.commitment) || other.commitment == _this.commitment)&&(identical(other.daScegliere, _this.daScegliere) || other.daScegliere == _this.daScegliere)&&const DeepCollectionEquality().equals(other.pickedSlots, _this.pickedSlots));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Ventaglio;
  return Object.hash(runtimeType,_this.slotCount,_this.commitment,_this.daScegliere,const DeepCollectionEquality().hash(_this.pickedSlots));
}

@override
String toString() {
  final _this = this as Ventaglio;
  return 'Ventaglio(slotCount: ${_this.slotCount}, commitment: ${_this.commitment}, daScegliere: ${_this.daScegliere}, pickedSlots: ${_this.pickedSlots})';
}


}

/// @nodoc
abstract mixin class $VentaglioCopyWith<$Res>  {
  factory $VentaglioCopyWith(Ventaglio value, $Res Function(Ventaglio) _then) = _$VentaglioCopyWithImpl;
@useResult
$Res call({
 int slotCount, String commitment, int daScegliere, List<int> pickedSlots
});




}
/// @nodoc
class _$VentaglioCopyWithImpl<$Res>
    implements $VentaglioCopyWith<$Res> {
  _$VentaglioCopyWithImpl(this._self, this._then);

  final Ventaglio _self;
  final $Res Function(Ventaglio) _then;

/// Create a copy of Ventaglio
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? slotCount = null,Object? commitment = null,Object? daScegliere = null,Object? pickedSlots = null,}) {
  return _then(Ventaglio(
slotCount: null == slotCount ? _self.slotCount : slotCount // ignore: cast_nullable_to_non_nullable
as int,commitment: null == commitment ? _self.commitment : commitment // ignore: cast_nullable_to_non_nullable
as String,daScegliere: null == daScegliere ? _self.daScegliere : daScegliere // ignore: cast_nullable_to_non_nullable
as int,pickedSlots: null == pickedSlots ? _self.pickedSlots : pickedSlots // ignore: cast_nullable_to_non_nullable
as List<int>,
  ));
}

}


/// Adds pattern-matching-related methods to [Ventaglio].
extension VentaglioPatterns on Ventaglio {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Ventaglio value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Ventaglio() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Ventaglio value)  $default,){
final _that = this;
switch (_that) {
case _Ventaglio():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Ventaglio value)?  $default,){
final _that = this;
switch (_that) {
case _Ventaglio() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int slotCount,  String commitment,  int daScegliere,  List<int> pickedSlots)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Ventaglio() when $default != null:
return $default(_that.slotCount,_that.commitment,_that.daScegliere,_that.pickedSlots);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int slotCount,  String commitment,  int daScegliere,  List<int> pickedSlots)  $default,) {final _that = this;
switch (_that) {
case _Ventaglio():
return $default(_that.slotCount,_that.commitment,_that.daScegliere,_that.pickedSlots);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int slotCount,  String commitment,  int daScegliere,  List<int> pickedSlots)?  $default,) {final _that = this;
switch (_that) {
case _Ventaglio() when $default != null:
return $default(_that.slotCount,_that.commitment,_that.daScegliere,_that.pickedSlots);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Ventaglio implements Ventaglio {
  const _Ventaglio({required this.slotCount, required this.commitment, required this.daScegliere,  List<int> pickedSlots = const <int>[]}): _pickedSlots = pickedSlots;
  factory _Ventaglio.fromJson(Map<String, dynamic> json) => _$VentaglioFromJson(json);

@override final  int slotCount;
@override final  String commitment;
@override final  int daScegliere;
 final  List<int> _pickedSlots;
@override@JsonKey() List<int> get pickedSlots {
  if (_pickedSlots is EqualUnmodifiableListView) return _pickedSlots;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_pickedSlots);
}


/// Create a copy of Ventaglio
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$VentaglioCopyWith<_Ventaglio> get copyWith => __$VentaglioCopyWithImpl<_Ventaglio>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$VentaglioToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Ventaglio&&(identical(other.slotCount, slotCount) || other.slotCount == slotCount)&&(identical(other.commitment, commitment) || other.commitment == commitment)&&(identical(other.daScegliere, daScegliere) || other.daScegliere == daScegliere)&&const DeepCollectionEquality().equals(other.pickedSlots, _pickedSlots));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,slotCount,commitment,daScegliere,const DeepCollectionEquality().hash(_pickedSlots));
}

@override
String toString() {
    return 'Ventaglio(slotCount: $slotCount, commitment: $commitment, daScegliere: $daScegliere, pickedSlots: $pickedSlots)';
}


}

/// @nodoc
abstract mixin class _$VentaglioCopyWith<$Res> implements $VentaglioCopyWith<$Res> {
  factory _$VentaglioCopyWith(_Ventaglio value, $Res Function(_Ventaglio) _then) = __$VentaglioCopyWithImpl;
@override @useResult
$Res call({
 int slotCount, String commitment, int daScegliere, List<int> pickedSlots
});




}
/// @nodoc
class __$VentaglioCopyWithImpl<$Res>
    implements _$VentaglioCopyWith<$Res> {
  __$VentaglioCopyWithImpl(this._self, this._then);

  final _Ventaglio _self;
  final $Res Function(_Ventaglio) _then;

/// Create a copy of Ventaglio
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? slotCount = null,Object? commitment = null,Object? daScegliere = null,Object? pickedSlots = null,}) {
  return _then(_Ventaglio(
slotCount: null == slotCount ? _self.slotCount : slotCount // ignore: cast_nullable_to_non_nullable
as int,commitment: null == commitment ? _self.commitment : commitment // ignore: cast_nullable_to_non_nullable
as String,daScegliere: null == daScegliere ? _self.daScegliere : daScegliere // ignore: cast_nullable_to_non_nullable
as int,pickedSlots: null == pickedSlots ? _self._pickedSlots : pickedSlots // ignore: cast_nullable_to_non_nullable
as List<int>,
  ));
}


}


/// @nodoc
mixin _$Scelta {

 int get posizione; int get slot; bool get tutteScelte; List<int> get posizioniCalcolate;
/// Create a copy of Scelta
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SceltaCopyWith<Scelta> get copyWith => _$SceltaCopyWithImpl<Scelta>(this as Scelta, _$identity);

  /// Serializes this Scelta to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Scelta;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Scelta&&(identical(other.posizione, _this.posizione) || other.posizione == _this.posizione)&&(identical(other.slot, _this.slot) || other.slot == _this.slot)&&(identical(other.tutteScelte, _this.tutteScelte) || other.tutteScelte == _this.tutteScelte)&&const DeepCollectionEquality().equals(other.posizioniCalcolate, _this.posizioniCalcolate));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Scelta;
  return Object.hash(runtimeType,_this.posizione,_this.slot,_this.tutteScelte,const DeepCollectionEquality().hash(_this.posizioniCalcolate));
}

@override
String toString() {
  final _this = this as Scelta;
  return 'Scelta(posizione: ${_this.posizione}, slot: ${_this.slot}, tutteScelte: ${_this.tutteScelte}, posizioniCalcolate: ${_this.posizioniCalcolate})';
}


}

/// @nodoc
abstract mixin class $SceltaCopyWith<$Res>  {
  factory $SceltaCopyWith(Scelta value, $Res Function(Scelta) _then) = _$SceltaCopyWithImpl;
@useResult
$Res call({
 int posizione, int slot, bool tutteScelte, List<int> posizioniCalcolate
});




}
/// @nodoc
class _$SceltaCopyWithImpl<$Res>
    implements $SceltaCopyWith<$Res> {
  _$SceltaCopyWithImpl(this._self, this._then);

  final Scelta _self;
  final $Res Function(Scelta) _then;

/// Create a copy of Scelta
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? posizione = null,Object? slot = null,Object? tutteScelte = null,Object? posizioniCalcolate = null,}) {
  return _then(Scelta(
posizione: null == posizione ? _self.posizione : posizione // ignore: cast_nullable_to_non_nullable
as int,slot: null == slot ? _self.slot : slot // ignore: cast_nullable_to_non_nullable
as int,tutteScelte: null == tutteScelte ? _self.tutteScelte : tutteScelte // ignore: cast_nullable_to_non_nullable
as bool,posizioniCalcolate: null == posizioniCalcolate ? _self.posizioniCalcolate : posizioniCalcolate // ignore: cast_nullable_to_non_nullable
as List<int>,
  ));
}

}


/// Adds pattern-matching-related methods to [Scelta].
extension SceltaPatterns on Scelta {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Scelta value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Scelta() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Scelta value)  $default,){
final _that = this;
switch (_that) {
case _Scelta():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Scelta value)?  $default,){
final _that = this;
switch (_that) {
case _Scelta() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int posizione,  int slot,  bool tutteScelte,  List<int> posizioniCalcolate)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Scelta() when $default != null:
return $default(_that.posizione,_that.slot,_that.tutteScelte,_that.posizioniCalcolate);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int posizione,  int slot,  bool tutteScelte,  List<int> posizioniCalcolate)  $default,) {final _that = this;
switch (_that) {
case _Scelta():
return $default(_that.posizione,_that.slot,_that.tutteScelte,_that.posizioniCalcolate);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int posizione,  int slot,  bool tutteScelte,  List<int> posizioniCalcolate)?  $default,) {final _that = this;
switch (_that) {
case _Scelta() when $default != null:
return $default(_that.posizione,_that.slot,_that.tutteScelte,_that.posizioniCalcolate);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Scelta implements Scelta {
  const _Scelta({required this.posizione, required this.slot, this.tutteScelte = false,  List<int> posizioniCalcolate = const <int>[]}): _posizioniCalcolate = posizioniCalcolate;
  factory _Scelta.fromJson(Map<String, dynamic> json) => _$SceltaFromJson(json);

@override final  int posizione;
@override final  int slot;
@override@JsonKey() final  bool tutteScelte;
 final  List<int> _posizioniCalcolate;
@override@JsonKey() List<int> get posizioniCalcolate {
  if (_posizioniCalcolate is EqualUnmodifiableListView) return _posizioniCalcolate;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_posizioniCalcolate);
}


/// Create a copy of Scelta
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SceltaCopyWith<_Scelta> get copyWith => __$SceltaCopyWithImpl<_Scelta>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SceltaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Scelta&&(identical(other.posizione, posizione) || other.posizione == posizione)&&(identical(other.slot, slot) || other.slot == slot)&&(identical(other.tutteScelte, tutteScelte) || other.tutteScelte == tutteScelte)&&const DeepCollectionEquality().equals(other.posizioniCalcolate, _posizioniCalcolate));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,posizione,slot,tutteScelte,const DeepCollectionEquality().hash(_posizioniCalcolate));
}

@override
String toString() {
    return 'Scelta(posizione: $posizione, slot: $slot, tutteScelte: $tutteScelte, posizioniCalcolate: $posizioniCalcolate)';
}


}

/// @nodoc
abstract mixin class _$SceltaCopyWith<$Res> implements $SceltaCopyWith<$Res> {
  factory _$SceltaCopyWith(_Scelta value, $Res Function(_Scelta) _then) = __$SceltaCopyWithImpl;
@override @useResult
$Res call({
 int posizione, int slot, bool tutteScelte, List<int> posizioniCalcolate
});




}
/// @nodoc
class __$SceltaCopyWithImpl<$Res>
    implements _$SceltaCopyWith<$Res> {
  __$SceltaCopyWithImpl(this._self, this._then);

  final _Scelta _self;
  final $Res Function(_Scelta) _then;

/// Create a copy of Scelta
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? posizione = null,Object? slot = null,Object? tutteScelte = null,Object? posizioniCalcolate = null,}) {
  return _then(_Scelta(
posizione: null == posizione ? _self.posizione : posizione // ignore: cast_nullable_to_non_nullable
as int,slot: null == slot ? _self.slot : slot // ignore: cast_nullable_to_non_nullable
as int,tutteScelte: null == tutteScelte ? _self.tutteScelte : tutteScelte // ignore: cast_nullable_to_non_nullable
as bool,posizioniCalcolate: null == posizioniCalcolate ? _self._posizioniCalcolate : posizioniCalcolate // ignore: cast_nullable_to_non_nullable
as List<int>,
  ));
}


}


/// @nodoc
mixin _$StatoCondivisione {

 String? get shareToken; String? get shareText;
/// Create a copy of StatoCondivisione
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$StatoCondivisioneCopyWith<StatoCondivisione> get copyWith => _$StatoCondivisioneCopyWithImpl<StatoCondivisione>(this as StatoCondivisione, _$identity);

  /// Serializes this StatoCondivisione to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as StatoCondivisione;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is StatoCondivisione&&(identical(other.shareToken, _this.shareToken) || other.shareToken == _this.shareToken)&&(identical(other.shareText, _this.shareText) || other.shareText == _this.shareText));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as StatoCondivisione;
  return Object.hash(runtimeType,_this.shareToken,_this.shareText);
}

@override
String toString() {
  final _this = this as StatoCondivisione;
  return 'StatoCondivisione(shareToken: ${_this.shareToken}, shareText: ${_this.shareText})';
}


}

/// @nodoc
abstract mixin class $StatoCondivisioneCopyWith<$Res>  {
  factory $StatoCondivisioneCopyWith(StatoCondivisione value, $Res Function(StatoCondivisione) _then) = _$StatoCondivisioneCopyWithImpl;
@useResult
$Res call({
 String? shareToken, String? shareText
});




}
/// @nodoc
class _$StatoCondivisioneCopyWithImpl<$Res>
    implements $StatoCondivisioneCopyWith<$Res> {
  _$StatoCondivisioneCopyWithImpl(this._self, this._then);

  final StatoCondivisione _self;
  final $Res Function(StatoCondivisione) _then;

/// Create a copy of StatoCondivisione
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? shareToken = freezed,Object? shareText = freezed,}) {
  return _then(StatoCondivisione(
shareToken: freezed == shareToken ? _self.shareToken : shareToken // ignore: cast_nullable_to_non_nullable
as String?,shareText: freezed == shareText ? _self.shareText : shareText // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [StatoCondivisione].
extension StatoCondivisionePatterns on StatoCondivisione {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _StatoCondivisione value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _StatoCondivisione() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _StatoCondivisione value)  $default,){
final _that = this;
switch (_that) {
case _StatoCondivisione():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _StatoCondivisione value)?  $default,){
final _that = this;
switch (_that) {
case _StatoCondivisione() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? shareToken,  String? shareText)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _StatoCondivisione() when $default != null:
return $default(_that.shareToken,_that.shareText);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? shareToken,  String? shareText)  $default,) {final _that = this;
switch (_that) {
case _StatoCondivisione():
return $default(_that.shareToken,_that.shareText);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? shareToken,  String? shareText)?  $default,) {final _that = this;
switch (_that) {
case _StatoCondivisione() when $default != null:
return $default(_that.shareToken,_that.shareText);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _StatoCondivisione implements StatoCondivisione {
  const _StatoCondivisione({this.shareToken, this.shareText});
  factory _StatoCondivisione.fromJson(Map<String, dynamic> json) => _$StatoCondivisioneFromJson(json);

@override final  String? shareToken;
@override final  String? shareText;

/// Create a copy of StatoCondivisione
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$StatoCondivisioneCopyWith<_StatoCondivisione> get copyWith => __$StatoCondivisioneCopyWithImpl<_StatoCondivisione>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$StatoCondivisioneToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _StatoCondivisione&&(identical(other.shareToken, shareToken) || other.shareToken == shareToken)&&(identical(other.shareText, shareText) || other.shareText == shareText));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,shareToken,shareText);
}

@override
String toString() {
    return 'StatoCondivisione(shareToken: $shareToken, shareText: $shareText)';
}


}

/// @nodoc
abstract mixin class _$StatoCondivisioneCopyWith<$Res> implements $StatoCondivisioneCopyWith<$Res> {
  factory _$StatoCondivisioneCopyWith(_StatoCondivisione value, $Res Function(_StatoCondivisione) _then) = __$StatoCondivisioneCopyWithImpl;
@override @useResult
$Res call({
 String? shareToken, String? shareText
});




}
/// @nodoc
class __$StatoCondivisioneCopyWithImpl<$Res>
    implements _$StatoCondivisioneCopyWith<$Res> {
  __$StatoCondivisioneCopyWithImpl(this._self, this._then);

  final _StatoCondivisione _self;
  final $Res Function(_StatoCondivisione) _then;

/// Create a copy of StatoCondivisione
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? shareToken = freezed,Object? shareText = freezed,}) {
  return _then(_StatoCondivisione(
shareToken: freezed == shareToken ? _self.shareToken : shareToken // ignore: cast_nullable_to_non_nullable
as String?,shareText: freezed == shareText ? _self.shareText : shareText // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$LetturaCondivisa {

 String get question; String? get mazzo; String get lang; Stesa? get stesa; String get categoria; bool get speciale;/// `venere`, `marte`, `mercurio`, `stella`.
 String? get partnerSimbolo; String? get partnerFrase; List<CartaPosata> get cards; String? get synthesis; String? get shareText; bool get immagine; String get createdAt; String get disclaimer;
/// Create a copy of LetturaCondivisa
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LetturaCondivisaCopyWith<LetturaCondivisa> get copyWith => _$LetturaCondivisaCopyWithImpl<LetturaCondivisa>(this as LetturaCondivisa, _$identity);

  /// Serializes this LetturaCondivisa to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as LetturaCondivisa;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is LetturaCondivisa&&(identical(other.question, _this.question) || other.question == _this.question)&&(identical(other.mazzo, _this.mazzo) || other.mazzo == _this.mazzo)&&(identical(other.lang, _this.lang) || other.lang == _this.lang)&&(identical(other.stesa, _this.stesa) || other.stesa == _this.stesa)&&(identical(other.categoria, _this.categoria) || other.categoria == _this.categoria)&&(identical(other.speciale, _this.speciale) || other.speciale == _this.speciale)&&(identical(other.partnerSimbolo, _this.partnerSimbolo) || other.partnerSimbolo == _this.partnerSimbolo)&&(identical(other.partnerFrase, _this.partnerFrase) || other.partnerFrase == _this.partnerFrase)&&const DeepCollectionEquality().equals(other.cards, _this.cards)&&(identical(other.synthesis, _this.synthesis) || other.synthesis == _this.synthesis)&&(identical(other.shareText, _this.shareText) || other.shareText == _this.shareText)&&(identical(other.immagine, _this.immagine) || other.immagine == _this.immagine)&&(identical(other.createdAt, _this.createdAt) || other.createdAt == _this.createdAt)&&(identical(other.disclaimer, _this.disclaimer) || other.disclaimer == _this.disclaimer));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as LetturaCondivisa;
  return Object.hash(runtimeType,_this.question,_this.mazzo,_this.lang,_this.stesa,_this.categoria,_this.speciale,_this.partnerSimbolo,_this.partnerFrase,const DeepCollectionEquality().hash(_this.cards),_this.synthesis,_this.shareText,_this.immagine,_this.createdAt,_this.disclaimer);
}

@override
String toString() {
  final _this = this as LetturaCondivisa;
  return 'LetturaCondivisa(question: ${_this.question}, mazzo: ${_this.mazzo}, lang: ${_this.lang}, stesa: ${_this.stesa}, categoria: ${_this.categoria}, speciale: ${_this.speciale}, partnerSimbolo: ${_this.partnerSimbolo}, partnerFrase: ${_this.partnerFrase}, cards: ${_this.cards}, synthesis: ${_this.synthesis}, shareText: ${_this.shareText}, immagine: ${_this.immagine}, createdAt: ${_this.createdAt}, disclaimer: ${_this.disclaimer})';
}


}

/// @nodoc
abstract mixin class $LetturaCondivisaCopyWith<$Res>  {
  factory $LetturaCondivisaCopyWith(LetturaCondivisa value, $Res Function(LetturaCondivisa) _then) = _$LetturaCondivisaCopyWithImpl;
@useResult
$Res call({
 String question, String? mazzo, String lang, Stesa? stesa, String categoria, bool speciale, String? partnerSimbolo, String? partnerFrase, List<CartaPosata> cards, String? synthesis, String? shareText, bool immagine, String createdAt, String disclaimer
});


$StesaCopyWith<$Res>? get stesa;

}
/// @nodoc
class _$LetturaCondivisaCopyWithImpl<$Res>
    implements $LetturaCondivisaCopyWith<$Res> {
  _$LetturaCondivisaCopyWithImpl(this._self, this._then);

  final LetturaCondivisa _self;
  final $Res Function(LetturaCondivisa) _then;

/// Create a copy of LetturaCondivisa
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? question = null,Object? mazzo = freezed,Object? lang = null,Object? stesa = freezed,Object? categoria = null,Object? speciale = null,Object? partnerSimbolo = freezed,Object? partnerFrase = freezed,Object? cards = null,Object? synthesis = freezed,Object? shareText = freezed,Object? immagine = null,Object? createdAt = null,Object? disclaimer = null,}) {
  return _then(LetturaCondivisa(
question: null == question ? _self.question : question // ignore: cast_nullable_to_non_nullable
as String,mazzo: freezed == mazzo ? _self.mazzo : mazzo // ignore: cast_nullable_to_non_nullable
as String?,lang: null == lang ? _self.lang : lang // ignore: cast_nullable_to_non_nullable
as String,stesa: freezed == stesa ? _self.stesa : stesa // ignore: cast_nullable_to_non_nullable
as Stesa?,categoria: null == categoria ? _self.categoria : categoria // ignore: cast_nullable_to_non_nullable
as String,speciale: null == speciale ? _self.speciale : speciale // ignore: cast_nullable_to_non_nullable
as bool,partnerSimbolo: freezed == partnerSimbolo ? _self.partnerSimbolo : partnerSimbolo // ignore: cast_nullable_to_non_nullable
as String?,partnerFrase: freezed == partnerFrase ? _self.partnerFrase : partnerFrase // ignore: cast_nullable_to_non_nullable
as String?,cards: null == cards ? _self.cards : cards // ignore: cast_nullable_to_non_nullable
as List<CartaPosata>,synthesis: freezed == synthesis ? _self.synthesis : synthesis // ignore: cast_nullable_to_non_nullable
as String?,shareText: freezed == shareText ? _self.shareText : shareText // ignore: cast_nullable_to_non_nullable
as String?,immagine: null == immagine ? _self.immagine : immagine // ignore: cast_nullable_to_non_nullable
as bool,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,disclaimer: null == disclaimer ? _self.disclaimer : disclaimer // ignore: cast_nullable_to_non_nullable
as String,
  ));
}
/// Create a copy of LetturaCondivisa
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$StesaCopyWith<$Res>? get stesa {
    if (_self.stesa == null) {
    return null;
  }

  return $StesaCopyWith<$Res>(_self.stesa!, (value) {
    return _then(_self.copyWith(stesa: value));
  });
}
}


/// Adds pattern-matching-related methods to [LetturaCondivisa].
extension LetturaCondivisaPatterns on LetturaCondivisa {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _LetturaCondivisa value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _LetturaCondivisa() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _LetturaCondivisa value)  $default,){
final _that = this;
switch (_that) {
case _LetturaCondivisa():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _LetturaCondivisa value)?  $default,){
final _that = this;
switch (_that) {
case _LetturaCondivisa() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String question,  String? mazzo,  String lang,  Stesa? stesa,  String categoria,  bool speciale,  String? partnerSimbolo,  String? partnerFrase,  List<CartaPosata> cards,  String? synthesis,  String? shareText,  bool immagine,  String createdAt,  String disclaimer)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _LetturaCondivisa() when $default != null:
return $default(_that.question,_that.mazzo,_that.lang,_that.stesa,_that.categoria,_that.speciale,_that.partnerSimbolo,_that.partnerFrase,_that.cards,_that.synthesis,_that.shareText,_that.immagine,_that.createdAt,_that.disclaimer);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String question,  String? mazzo,  String lang,  Stesa? stesa,  String categoria,  bool speciale,  String? partnerSimbolo,  String? partnerFrase,  List<CartaPosata> cards,  String? synthesis,  String? shareText,  bool immagine,  String createdAt,  String disclaimer)  $default,) {final _that = this;
switch (_that) {
case _LetturaCondivisa():
return $default(_that.question,_that.mazzo,_that.lang,_that.stesa,_that.categoria,_that.speciale,_that.partnerSimbolo,_that.partnerFrase,_that.cards,_that.synthesis,_that.shareText,_that.immagine,_that.createdAt,_that.disclaimer);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String question,  String? mazzo,  String lang,  Stesa? stesa,  String categoria,  bool speciale,  String? partnerSimbolo,  String? partnerFrase,  List<CartaPosata> cards,  String? synthesis,  String? shareText,  bool immagine,  String createdAt,  String disclaimer)?  $default,) {final _that = this;
switch (_that) {
case _LetturaCondivisa() when $default != null:
return $default(_that.question,_that.mazzo,_that.lang,_that.stesa,_that.categoria,_that.speciale,_that.partnerSimbolo,_that.partnerFrase,_that.cards,_that.synthesis,_that.shareText,_that.immagine,_that.createdAt,_that.disclaimer);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _LetturaCondivisa implements LetturaCondivisa {
  const _LetturaCondivisa({required this.question, this.mazzo, required this.lang, this.stesa, required this.categoria, this.speciale = false, this.partnerSimbolo, this.partnerFrase,  List<CartaPosata> cards = const <CartaPosata>[], this.synthesis, this.shareText, this.immagine = false, required this.createdAt, this.disclaimer = ''}): _cards = cards;
  factory _LetturaCondivisa.fromJson(Map<String, dynamic> json) => _$LetturaCondivisaFromJson(json);

@override final  String question;
@override final  String? mazzo;
@override final  String lang;
@override final  Stesa? stesa;
@override final  String categoria;
@override@JsonKey() final  bool speciale;
/// `venere`, `marte`, `mercurio`, `stella`.
@override final  String? partnerSimbolo;
@override final  String? partnerFrase;
 final  List<CartaPosata> _cards;
@override@JsonKey() List<CartaPosata> get cards {
  if (_cards is EqualUnmodifiableListView) return _cards;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_cards);
}

@override final  String? synthesis;
@override final  String? shareText;
@override@JsonKey() final  bool immagine;
@override final  String createdAt;
@override@JsonKey() final  String disclaimer;

/// Create a copy of LetturaCondivisa
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$LetturaCondivisaCopyWith<_LetturaCondivisa> get copyWith => __$LetturaCondivisaCopyWithImpl<_LetturaCondivisa>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$LetturaCondivisaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _LetturaCondivisa&&(identical(other.question, question) || other.question == question)&&(identical(other.mazzo, mazzo) || other.mazzo == mazzo)&&(identical(other.lang, lang) || other.lang == lang)&&(identical(other.stesa, stesa) || other.stesa == stesa)&&(identical(other.categoria, categoria) || other.categoria == categoria)&&(identical(other.speciale, speciale) || other.speciale == speciale)&&(identical(other.partnerSimbolo, partnerSimbolo) || other.partnerSimbolo == partnerSimbolo)&&(identical(other.partnerFrase, partnerFrase) || other.partnerFrase == partnerFrase)&&const DeepCollectionEquality().equals(other.cards, _cards)&&(identical(other.synthesis, synthesis) || other.synthesis == synthesis)&&(identical(other.shareText, shareText) || other.shareText == shareText)&&(identical(other.immagine, immagine) || other.immagine == immagine)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.disclaimer, disclaimer) || other.disclaimer == disclaimer));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,question,mazzo,lang,stesa,categoria,speciale,partnerSimbolo,partnerFrase,const DeepCollectionEquality().hash(_cards),synthesis,shareText,immagine,createdAt,disclaimer);
}

@override
String toString() {
    return 'LetturaCondivisa(question: $question, mazzo: $mazzo, lang: $lang, stesa: $stesa, categoria: $categoria, speciale: $speciale, partnerSimbolo: $partnerSimbolo, partnerFrase: $partnerFrase, cards: $cards, synthesis: $synthesis, shareText: $shareText, immagine: $immagine, createdAt: $createdAt, disclaimer: $disclaimer)';
}


}

/// @nodoc
abstract mixin class _$LetturaCondivisaCopyWith<$Res> implements $LetturaCondivisaCopyWith<$Res> {
  factory _$LetturaCondivisaCopyWith(_LetturaCondivisa value, $Res Function(_LetturaCondivisa) _then) = __$LetturaCondivisaCopyWithImpl;
@override @useResult
$Res call({
 String question, String? mazzo, String lang, Stesa? stesa, String categoria, bool speciale, String? partnerSimbolo, String? partnerFrase, List<CartaPosata> cards, String? synthesis, String? shareText, bool immagine, String createdAt, String disclaimer
});


@override $StesaCopyWith<$Res>? get stesa;

}
/// @nodoc
class __$LetturaCondivisaCopyWithImpl<$Res>
    implements _$LetturaCondivisaCopyWith<$Res> {
  __$LetturaCondivisaCopyWithImpl(this._self, this._then);

  final _LetturaCondivisa _self;
  final $Res Function(_LetturaCondivisa) _then;

/// Create a copy of LetturaCondivisa
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? question = null,Object? mazzo = freezed,Object? lang = null,Object? stesa = freezed,Object? categoria = null,Object? speciale = null,Object? partnerSimbolo = freezed,Object? partnerFrase = freezed,Object? cards = null,Object? synthesis = freezed,Object? shareText = freezed,Object? immagine = null,Object? createdAt = null,Object? disclaimer = null,}) {
  return _then(_LetturaCondivisa(
question: null == question ? _self.question : question // ignore: cast_nullable_to_non_nullable
as String,mazzo: freezed == mazzo ? _self.mazzo : mazzo // ignore: cast_nullable_to_non_nullable
as String?,lang: null == lang ? _self.lang : lang // ignore: cast_nullable_to_non_nullable
as String,stesa: freezed == stesa ? _self.stesa : stesa // ignore: cast_nullable_to_non_nullable
as Stesa?,categoria: null == categoria ? _self.categoria : categoria // ignore: cast_nullable_to_non_nullable
as String,speciale: null == speciale ? _self.speciale : speciale // ignore: cast_nullable_to_non_nullable
as bool,partnerSimbolo: freezed == partnerSimbolo ? _self.partnerSimbolo : partnerSimbolo // ignore: cast_nullable_to_non_nullable
as String?,partnerFrase: freezed == partnerFrase ? _self.partnerFrase : partnerFrase // ignore: cast_nullable_to_non_nullable
as String?,cards: null == cards ? _self._cards : cards // ignore: cast_nullable_to_non_nullable
as List<CartaPosata>,synthesis: freezed == synthesis ? _self.synthesis : synthesis // ignore: cast_nullable_to_non_nullable
as String?,shareText: freezed == shareText ? _self.shareText : shareText // ignore: cast_nullable_to_non_nullable
as String?,immagine: null == immagine ? _self.immagine : immagine // ignore: cast_nullable_to_non_nullable
as bool,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,disclaimer: null == disclaimer ? _self.disclaimer : disclaimer // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

/// Create a copy of LetturaCondivisa
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$StesaCopyWith<$Res>? get stesa {
    if (_self.stesa == null) {
    return null;
  }

  return $StesaCopyWith<$Res>(_self.stesa!, (value) {
    return _then(_self.copyWith(stesa: value));
  });
}
}


/// @nodoc
mixin _$Memoria {

 String get id; String get contenuto;/// `stabile` o `variabile`.
 String get tipo; String get campoAttinenza;/// `lettura` o `chat`.
 String get fonte; String? get aggiornata;
/// Create a copy of Memoria
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MemoriaCopyWith<Memoria> get copyWith => _$MemoriaCopyWithImpl<Memoria>(this as Memoria, _$identity);

  /// Serializes this Memoria to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Memoria;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Memoria&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.contenuto, _this.contenuto) || other.contenuto == _this.contenuto)&&(identical(other.tipo, _this.tipo) || other.tipo == _this.tipo)&&(identical(other.campoAttinenza, _this.campoAttinenza) || other.campoAttinenza == _this.campoAttinenza)&&(identical(other.fonte, _this.fonte) || other.fonte == _this.fonte)&&(identical(other.aggiornata, _this.aggiornata) || other.aggiornata == _this.aggiornata));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Memoria;
  return Object.hash(runtimeType,_this.id,_this.contenuto,_this.tipo,_this.campoAttinenza,_this.fonte,_this.aggiornata);
}

@override
String toString() {
  final _this = this as Memoria;
  return 'Memoria(id: ${_this.id}, contenuto: ${_this.contenuto}, tipo: ${_this.tipo}, campoAttinenza: ${_this.campoAttinenza}, fonte: ${_this.fonte}, aggiornata: ${_this.aggiornata})';
}


}

/// @nodoc
abstract mixin class $MemoriaCopyWith<$Res>  {
  factory $MemoriaCopyWith(Memoria value, $Res Function(Memoria) _then) = _$MemoriaCopyWithImpl;
@useResult
$Res call({
 String id, String contenuto, String tipo, String campoAttinenza, String fonte, String? aggiornata
});




}
/// @nodoc
class _$MemoriaCopyWithImpl<$Res>
    implements $MemoriaCopyWith<$Res> {
  _$MemoriaCopyWithImpl(this._self, this._then);

  final Memoria _self;
  final $Res Function(Memoria) _then;

/// Create a copy of Memoria
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? contenuto = null,Object? tipo = null,Object? campoAttinenza = null,Object? fonte = null,Object? aggiornata = freezed,}) {
  return _then(Memoria(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,contenuto: null == contenuto ? _self.contenuto : contenuto // ignore: cast_nullable_to_non_nullable
as String,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,campoAttinenza: null == campoAttinenza ? _self.campoAttinenza : campoAttinenza // ignore: cast_nullable_to_non_nullable
as String,fonte: null == fonte ? _self.fonte : fonte // ignore: cast_nullable_to_non_nullable
as String,aggiornata: freezed == aggiornata ? _self.aggiornata : aggiornata // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [Memoria].
extension MemoriaPatterns on Memoria {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Memoria value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Memoria() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Memoria value)  $default,){
final _that = this;
switch (_that) {
case _Memoria():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Memoria value)?  $default,){
final _that = this;
switch (_that) {
case _Memoria() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String contenuto,  String tipo,  String campoAttinenza,  String fonte,  String? aggiornata)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Memoria() when $default != null:
return $default(_that.id,_that.contenuto,_that.tipo,_that.campoAttinenza,_that.fonte,_that.aggiornata);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String contenuto,  String tipo,  String campoAttinenza,  String fonte,  String? aggiornata)  $default,) {final _that = this;
switch (_that) {
case _Memoria():
return $default(_that.id,_that.contenuto,_that.tipo,_that.campoAttinenza,_that.fonte,_that.aggiornata);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String contenuto,  String tipo,  String campoAttinenza,  String fonte,  String? aggiornata)?  $default,) {final _that = this;
switch (_that) {
case _Memoria() when $default != null:
return $default(_that.id,_that.contenuto,_that.tipo,_that.campoAttinenza,_that.fonte,_that.aggiornata);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Memoria implements Memoria {
  const _Memoria({required this.id, required this.contenuto, required this.tipo, required this.campoAttinenza, required this.fonte, this.aggiornata});
  factory _Memoria.fromJson(Map<String, dynamic> json) => _$MemoriaFromJson(json);

@override final  String id;
@override final  String contenuto;
/// `stabile` o `variabile`.
@override final  String tipo;
@override final  String campoAttinenza;
/// `lettura` o `chat`.
@override final  String fonte;
@override final  String? aggiornata;

/// Create a copy of Memoria
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MemoriaCopyWith<_Memoria> get copyWith => __$MemoriaCopyWithImpl<_Memoria>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MemoriaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Memoria&&(identical(other.id, id) || other.id == id)&&(identical(other.contenuto, contenuto) || other.contenuto == contenuto)&&(identical(other.tipo, tipo) || other.tipo == tipo)&&(identical(other.campoAttinenza, campoAttinenza) || other.campoAttinenza == campoAttinenza)&&(identical(other.fonte, fonte) || other.fonte == fonte)&&(identical(other.aggiornata, aggiornata) || other.aggiornata == aggiornata));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,contenuto,tipo,campoAttinenza,fonte,aggiornata);
}

@override
String toString() {
    return 'Memoria(id: $id, contenuto: $contenuto, tipo: $tipo, campoAttinenza: $campoAttinenza, fonte: $fonte, aggiornata: $aggiornata)';
}


}

/// @nodoc
abstract mixin class _$MemoriaCopyWith<$Res> implements $MemoriaCopyWith<$Res> {
  factory _$MemoriaCopyWith(_Memoria value, $Res Function(_Memoria) _then) = __$MemoriaCopyWithImpl;
@override @useResult
$Res call({
 String id, String contenuto, String tipo, String campoAttinenza, String fonte, String? aggiornata
});




}
/// @nodoc
class __$MemoriaCopyWithImpl<$Res>
    implements _$MemoriaCopyWith<$Res> {
  __$MemoriaCopyWithImpl(this._self, this._then);

  final _Memoria _self;
  final $Res Function(_Memoria) _then;

/// Create a copy of Memoria
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? contenuto = null,Object? tipo = null,Object? campoAttinenza = null,Object? fonte = null,Object? aggiornata = freezed,}) {
  return _then(_Memoria(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,contenuto: null == contenuto ? _self.contenuto : contenuto // ignore: cast_nullable_to_non_nullable
as String,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,campoAttinenza: null == campoAttinenza ? _self.campoAttinenza : campoAttinenza // ignore: cast_nullable_to_non_nullable
as String,fonte: null == fonte ? _self.fonte : fonte // ignore: cast_nullable_to_non_nullable
as String,aggiornata: freezed == aggiornata ? _self.aggiornata : aggiornata // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$PropostaLettura {

 String get argomento; String get categoria;
/// Create a copy of PropostaLettura
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PropostaLetturaCopyWith<PropostaLettura> get copyWith => _$PropostaLetturaCopyWithImpl<PropostaLettura>(this as PropostaLettura, _$identity);

  /// Serializes this PropostaLettura to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as PropostaLettura;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PropostaLettura&&(identical(other.argomento, _this.argomento) || other.argomento == _this.argomento)&&(identical(other.categoria, _this.categoria) || other.categoria == _this.categoria));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as PropostaLettura;
  return Object.hash(runtimeType,_this.argomento,_this.categoria);
}

@override
String toString() {
  final _this = this as PropostaLettura;
  return 'PropostaLettura(argomento: ${_this.argomento}, categoria: ${_this.categoria})';
}


}

/// @nodoc
abstract mixin class $PropostaLetturaCopyWith<$Res>  {
  factory $PropostaLetturaCopyWith(PropostaLettura value, $Res Function(PropostaLettura) _then) = _$PropostaLetturaCopyWithImpl;
@useResult
$Res call({
 String argomento, String categoria
});




}
/// @nodoc
class _$PropostaLetturaCopyWithImpl<$Res>
    implements $PropostaLetturaCopyWith<$Res> {
  _$PropostaLetturaCopyWithImpl(this._self, this._then);

  final PropostaLettura _self;
  final $Res Function(PropostaLettura) _then;

/// Create a copy of PropostaLettura
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? argomento = null,Object? categoria = null,}) {
  return _then(PropostaLettura(
argomento: null == argomento ? _self.argomento : argomento // ignore: cast_nullable_to_non_nullable
as String,categoria: null == categoria ? _self.categoria : categoria // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [PropostaLettura].
extension PropostaLetturaPatterns on PropostaLettura {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PropostaLettura value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PropostaLettura() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PropostaLettura value)  $default,){
final _that = this;
switch (_that) {
case _PropostaLettura():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PropostaLettura value)?  $default,){
final _that = this;
switch (_that) {
case _PropostaLettura() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String argomento,  String categoria)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PropostaLettura() when $default != null:
return $default(_that.argomento,_that.categoria);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String argomento,  String categoria)  $default,) {final _that = this;
switch (_that) {
case _PropostaLettura():
return $default(_that.argomento,_that.categoria);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String argomento,  String categoria)?  $default,) {final _that = this;
switch (_that) {
case _PropostaLettura() when $default != null:
return $default(_that.argomento,_that.categoria);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _PropostaLettura implements PropostaLettura {
  const _PropostaLettura({required this.argomento, required this.categoria});
  factory _PropostaLettura.fromJson(Map<String, dynamic> json) => _$PropostaLetturaFromJson(json);

@override final  String argomento;
@override final  String categoria;

/// Create a copy of PropostaLettura
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PropostaLetturaCopyWith<_PropostaLettura> get copyWith => __$PropostaLetturaCopyWithImpl<_PropostaLettura>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PropostaLetturaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _PropostaLettura&&(identical(other.argomento, argomento) || other.argomento == argomento)&&(identical(other.categoria, categoria) || other.categoria == categoria));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,argomento,categoria);
}

@override
String toString() {
    return 'PropostaLettura(argomento: $argomento, categoria: $categoria)';
}


}

/// @nodoc
abstract mixin class _$PropostaLetturaCopyWith<$Res> implements $PropostaLetturaCopyWith<$Res> {
  factory _$PropostaLetturaCopyWith(_PropostaLettura value, $Res Function(_PropostaLettura) _then) = __$PropostaLetturaCopyWithImpl;
@override @useResult
$Res call({
 String argomento, String categoria
});




}
/// @nodoc
class __$PropostaLetturaCopyWithImpl<$Res>
    implements _$PropostaLetturaCopyWith<$Res> {
  __$PropostaLetturaCopyWithImpl(this._self, this._then);

  final _PropostaLettura _self;
  final $Res Function(_PropostaLettura) _then;

/// Create a copy of PropostaLettura
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? argomento = null,Object? categoria = null,}) {
  return _then(_PropostaLettura(
argomento: null == argomento ? _self.argomento : argomento // ignore: cast_nullable_to_non_nullable
as String,categoria: null == categoria ? _self.categoria : categoria // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$TurnoChat {

 String get id;/// `ai` o `utente`.
 String get ruolo; String get testo; PropostaLettura? get proposta; String? get creato;
/// Create a copy of TurnoChat
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$TurnoChatCopyWith<TurnoChat> get copyWith => _$TurnoChatCopyWithImpl<TurnoChat>(this as TurnoChat, _$identity);

  /// Serializes this TurnoChat to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as TurnoChat;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is TurnoChat&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.ruolo, _this.ruolo) || other.ruolo == _this.ruolo)&&(identical(other.testo, _this.testo) || other.testo == _this.testo)&&(identical(other.proposta, _this.proposta) || other.proposta == _this.proposta)&&(identical(other.creato, _this.creato) || other.creato == _this.creato));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as TurnoChat;
  return Object.hash(runtimeType,_this.id,_this.ruolo,_this.testo,_this.proposta,_this.creato);
}

@override
String toString() {
  final _this = this as TurnoChat;
  return 'TurnoChat(id: ${_this.id}, ruolo: ${_this.ruolo}, testo: ${_this.testo}, proposta: ${_this.proposta}, creato: ${_this.creato})';
}


}

/// @nodoc
abstract mixin class $TurnoChatCopyWith<$Res>  {
  factory $TurnoChatCopyWith(TurnoChat value, $Res Function(TurnoChat) _then) = _$TurnoChatCopyWithImpl;
@useResult
$Res call({
 String id, String ruolo, String testo, PropostaLettura? proposta, String? creato
});


$PropostaLetturaCopyWith<$Res>? get proposta;

}
/// @nodoc
class _$TurnoChatCopyWithImpl<$Res>
    implements $TurnoChatCopyWith<$Res> {
  _$TurnoChatCopyWithImpl(this._self, this._then);

  final TurnoChat _self;
  final $Res Function(TurnoChat) _then;

/// Create a copy of TurnoChat
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? ruolo = null,Object? testo = null,Object? proposta = freezed,Object? creato = freezed,}) {
  return _then(TurnoChat(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,ruolo: null == ruolo ? _self.ruolo : ruolo // ignore: cast_nullable_to_non_nullable
as String,testo: null == testo ? _self.testo : testo // ignore: cast_nullable_to_non_nullable
as String,proposta: freezed == proposta ? _self.proposta : proposta // ignore: cast_nullable_to_non_nullable
as PropostaLettura?,creato: freezed == creato ? _self.creato : creato // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}
/// Create a copy of TurnoChat
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PropostaLetturaCopyWith<$Res>? get proposta {
    if (_self.proposta == null) {
    return null;
  }

  return $PropostaLetturaCopyWith<$Res>(_self.proposta!, (value) {
    return _then(_self.copyWith(proposta: value));
  });
}
}


/// Adds pattern-matching-related methods to [TurnoChat].
extension TurnoChatPatterns on TurnoChat {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _TurnoChat value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _TurnoChat() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _TurnoChat value)  $default,){
final _that = this;
switch (_that) {
case _TurnoChat():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _TurnoChat value)?  $default,){
final _that = this;
switch (_that) {
case _TurnoChat() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String ruolo,  String testo,  PropostaLettura? proposta,  String? creato)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _TurnoChat() when $default != null:
return $default(_that.id,_that.ruolo,_that.testo,_that.proposta,_that.creato);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String ruolo,  String testo,  PropostaLettura? proposta,  String? creato)  $default,) {final _that = this;
switch (_that) {
case _TurnoChat():
return $default(_that.id,_that.ruolo,_that.testo,_that.proposta,_that.creato);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String ruolo,  String testo,  PropostaLettura? proposta,  String? creato)?  $default,) {final _that = this;
switch (_that) {
case _TurnoChat() when $default != null:
return $default(_that.id,_that.ruolo,_that.testo,_that.proposta,_that.creato);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _TurnoChat implements TurnoChat {
  const _TurnoChat({required this.id, required this.ruolo, required this.testo, this.proposta, this.creato});
  factory _TurnoChat.fromJson(Map<String, dynamic> json) => _$TurnoChatFromJson(json);

@override final  String id;
/// `ai` o `utente`.
@override final  String ruolo;
@override final  String testo;
@override final  PropostaLettura? proposta;
@override final  String? creato;

/// Create a copy of TurnoChat
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$TurnoChatCopyWith<_TurnoChat> get copyWith => __$TurnoChatCopyWithImpl<_TurnoChat>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$TurnoChatToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _TurnoChat&&(identical(other.id, id) || other.id == id)&&(identical(other.ruolo, ruolo) || other.ruolo == ruolo)&&(identical(other.testo, testo) || other.testo == testo)&&(identical(other.proposta, proposta) || other.proposta == proposta)&&(identical(other.creato, creato) || other.creato == creato));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,ruolo,testo,proposta,creato);
}

@override
String toString() {
    return 'TurnoChat(id: $id, ruolo: $ruolo, testo: $testo, proposta: $proposta, creato: $creato)';
}


}

/// @nodoc
abstract mixin class _$TurnoChatCopyWith<$Res> implements $TurnoChatCopyWith<$Res> {
  factory _$TurnoChatCopyWith(_TurnoChat value, $Res Function(_TurnoChat) _then) = __$TurnoChatCopyWithImpl;
@override @useResult
$Res call({
 String id, String ruolo, String testo, PropostaLettura? proposta, String? creato
});


@override $PropostaLetturaCopyWith<$Res>? get proposta;

}
/// @nodoc
class __$TurnoChatCopyWithImpl<$Res>
    implements _$TurnoChatCopyWith<$Res> {
  __$TurnoChatCopyWithImpl(this._self, this._then);

  final _TurnoChat _self;
  final $Res Function(_TurnoChat) _then;

/// Create a copy of TurnoChat
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? ruolo = null,Object? testo = null,Object? proposta = freezed,Object? creato = freezed,}) {
  return _then(_TurnoChat(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,ruolo: null == ruolo ? _self.ruolo : ruolo // ignore: cast_nullable_to_non_nullable
as String,testo: null == testo ? _self.testo : testo // ignore: cast_nullable_to_non_nullable
as String,proposta: freezed == proposta ? _self.proposta : proposta // ignore: cast_nullable_to_non_nullable
as PropostaLettura?,creato: freezed == creato ? _self.creato : creato // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of TurnoChat
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PropostaLetturaCopyWith<$Res>? get proposta {
    if (_self.proposta == null) {
    return null;
  }

  return $PropostaLetturaCopyWith<$Res>(_self.proposta!, (value) {
    return _then(_self.copyWith(proposta: value));
  });
}
}


/// @nodoc
mixin _$ImpostazioniChat {

 int get proattivaMinutiInattivita; int get proattivaMaxPerVisita;
/// Create a copy of ImpostazioniChat
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ImpostazioniChatCopyWith<ImpostazioniChat> get copyWith => _$ImpostazioniChatCopyWithImpl<ImpostazioniChat>(this as ImpostazioniChat, _$identity);

  /// Serializes this ImpostazioniChat to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as ImpostazioniChat;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ImpostazioniChat&&(identical(other.proattivaMinutiInattivita, _this.proattivaMinutiInattivita) || other.proattivaMinutiInattivita == _this.proattivaMinutiInattivita)&&(identical(other.proattivaMaxPerVisita, _this.proattivaMaxPerVisita) || other.proattivaMaxPerVisita == _this.proattivaMaxPerVisita));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as ImpostazioniChat;
  return Object.hash(runtimeType,_this.proattivaMinutiInattivita,_this.proattivaMaxPerVisita);
}

@override
String toString() {
  final _this = this as ImpostazioniChat;
  return 'ImpostazioniChat(proattivaMinutiInattivita: ${_this.proattivaMinutiInattivita}, proattivaMaxPerVisita: ${_this.proattivaMaxPerVisita})';
}


}

/// @nodoc
abstract mixin class $ImpostazioniChatCopyWith<$Res>  {
  factory $ImpostazioniChatCopyWith(ImpostazioniChat value, $Res Function(ImpostazioniChat) _then) = _$ImpostazioniChatCopyWithImpl;
@useResult
$Res call({
 int proattivaMinutiInattivita, int proattivaMaxPerVisita
});




}
/// @nodoc
class _$ImpostazioniChatCopyWithImpl<$Res>
    implements $ImpostazioniChatCopyWith<$Res> {
  _$ImpostazioniChatCopyWithImpl(this._self, this._then);

  final ImpostazioniChat _self;
  final $Res Function(ImpostazioniChat) _then;

/// Create a copy of ImpostazioniChat
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? proattivaMinutiInattivita = null,Object? proattivaMaxPerVisita = null,}) {
  return _then(ImpostazioniChat(
proattivaMinutiInattivita: null == proattivaMinutiInattivita ? _self.proattivaMinutiInattivita : proattivaMinutiInattivita // ignore: cast_nullable_to_non_nullable
as int,proattivaMaxPerVisita: null == proattivaMaxPerVisita ? _self.proattivaMaxPerVisita : proattivaMaxPerVisita // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [ImpostazioniChat].
extension ImpostazioniChatPatterns on ImpostazioniChat {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ImpostazioniChat value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ImpostazioniChat() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ImpostazioniChat value)  $default,){
final _that = this;
switch (_that) {
case _ImpostazioniChat():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ImpostazioniChat value)?  $default,){
final _that = this;
switch (_that) {
case _ImpostazioniChat() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int proattivaMinutiInattivita,  int proattivaMaxPerVisita)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ImpostazioniChat() when $default != null:
return $default(_that.proattivaMinutiInattivita,_that.proattivaMaxPerVisita);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int proattivaMinutiInattivita,  int proattivaMaxPerVisita)  $default,) {final _that = this;
switch (_that) {
case _ImpostazioniChat():
return $default(_that.proattivaMinutiInattivita,_that.proattivaMaxPerVisita);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int proattivaMinutiInattivita,  int proattivaMaxPerVisita)?  $default,) {final _that = this;
switch (_that) {
case _ImpostazioniChat() when $default != null:
return $default(_that.proattivaMinutiInattivita,_that.proattivaMaxPerVisita);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ImpostazioniChat implements ImpostazioniChat {
  const _ImpostazioniChat({this.proattivaMinutiInattivita = 30, this.proattivaMaxPerVisita = 3});
  factory _ImpostazioniChat.fromJson(Map<String, dynamic> json) => _$ImpostazioniChatFromJson(json);

@override@JsonKey() final  int proattivaMinutiInattivita;
@override@JsonKey() final  int proattivaMaxPerVisita;

/// Create a copy of ImpostazioniChat
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ImpostazioniChatCopyWith<_ImpostazioniChat> get copyWith => __$ImpostazioniChatCopyWithImpl<_ImpostazioniChat>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ImpostazioniChatToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _ImpostazioniChat&&(identical(other.proattivaMinutiInattivita, proattivaMinutiInattivita) || other.proattivaMinutiInattivita == proattivaMinutiInattivita)&&(identical(other.proattivaMaxPerVisita, proattivaMaxPerVisita) || other.proattivaMaxPerVisita == proattivaMaxPerVisita));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,proattivaMinutiInattivita,proattivaMaxPerVisita);
}

@override
String toString() {
    return 'ImpostazioniChat(proattivaMinutiInattivita: $proattivaMinutiInattivita, proattivaMaxPerVisita: $proattivaMaxPerVisita)';
}


}

/// @nodoc
abstract mixin class _$ImpostazioniChatCopyWith<$Res> implements $ImpostazioniChatCopyWith<$Res> {
  factory _$ImpostazioniChatCopyWith(_ImpostazioniChat value, $Res Function(_ImpostazioniChat) _then) = __$ImpostazioniChatCopyWithImpl;
@override @useResult
$Res call({
 int proattivaMinutiInattivita, int proattivaMaxPerVisita
});




}
/// @nodoc
class __$ImpostazioniChatCopyWithImpl<$Res>
    implements _$ImpostazioniChatCopyWith<$Res> {
  __$ImpostazioniChatCopyWithImpl(this._self, this._then);

  final _ImpostazioniChat _self;
  final $Res Function(_ImpostazioniChat) _then;

/// Create a copy of ImpostazioniChat
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? proattivaMinutiInattivita = null,Object? proattivaMaxPerVisita = null,}) {
  return _then(_ImpostazioniChat(
proattivaMinutiInattivita: null == proattivaMinutiInattivita ? _self.proattivaMinutiInattivita : proattivaMinutiInattivita // ignore: cast_nullable_to_non_nullable
as int,proattivaMaxPerVisita: null == proattivaMaxPerVisita ? _self.proattivaMaxPerVisita : proattivaMaxPerVisita // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}

// dart format on

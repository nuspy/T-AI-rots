// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'pubblici.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$CartaOggi {

 String get giorno; Carta get carta; String get testo;
/// Create a copy of CartaOggi
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CartaOggiCopyWith<CartaOggi> get copyWith => _$CartaOggiCopyWithImpl<CartaOggi>(this as CartaOggi, _$identity);

  /// Serializes this CartaOggi to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as CartaOggi;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CartaOggi&&(identical(other.giorno, _this.giorno) || other.giorno == _this.giorno)&&(identical(other.carta, _this.carta) || other.carta == _this.carta)&&(identical(other.testo, _this.testo) || other.testo == _this.testo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as CartaOggi;
  return Object.hash(runtimeType,_this.giorno,_this.carta,_this.testo);
}

@override
String toString() {
  final _this = this as CartaOggi;
  return 'CartaOggi(giorno: ${_this.giorno}, carta: ${_this.carta}, testo: ${_this.testo})';
}


}

/// @nodoc
abstract mixin class $CartaOggiCopyWith<$Res>  {
  factory $CartaOggiCopyWith(CartaOggi value, $Res Function(CartaOggi) _then) = _$CartaOggiCopyWithImpl;
@useResult
$Res call({
 String giorno, Carta carta, String testo
});


$CartaCopyWith<$Res> get carta;

}
/// @nodoc
class _$CartaOggiCopyWithImpl<$Res>
    implements $CartaOggiCopyWith<$Res> {
  _$CartaOggiCopyWithImpl(this._self, this._then);

  final CartaOggi _self;
  final $Res Function(CartaOggi) _then;

/// Create a copy of CartaOggi
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? giorno = null,Object? carta = null,Object? testo = null,}) {
  return _then(CartaOggi(
giorno: null == giorno ? _self.giorno : giorno // ignore: cast_nullable_to_non_nullable
as String,carta: null == carta ? _self.carta : carta // ignore: cast_nullable_to_non_nullable
as Carta,testo: null == testo ? _self.testo : testo // ignore: cast_nullable_to_non_nullable
as String,
  ));
}
/// Create a copy of CartaOggi
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CartaCopyWith<$Res> get carta {
  
  return $CartaCopyWith<$Res>(_self.carta, (value) {
    return _then(_self.copyWith(carta: value));
  });
}
}


/// Adds pattern-matching-related methods to [CartaOggi].
extension CartaOggiPatterns on CartaOggi {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CartaOggi value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CartaOggi() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CartaOggi value)  $default,){
final _that = this;
switch (_that) {
case _CartaOggi():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CartaOggi value)?  $default,){
final _that = this;
switch (_that) {
case _CartaOggi() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String giorno,  Carta carta,  String testo)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CartaOggi() when $default != null:
return $default(_that.giorno,_that.carta,_that.testo);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String giorno,  Carta carta,  String testo)  $default,) {final _that = this;
switch (_that) {
case _CartaOggi():
return $default(_that.giorno,_that.carta,_that.testo);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String giorno,  Carta carta,  String testo)?  $default,) {final _that = this;
switch (_that) {
case _CartaOggi() when $default != null:
return $default(_that.giorno,_that.carta,_that.testo);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CartaOggi implements CartaOggi {
  const _CartaOggi({required this.giorno, required this.carta, required this.testo});
  factory _CartaOggi.fromJson(Map<String, dynamic> json) => _$CartaOggiFromJson(json);

@override final  String giorno;
@override final  Carta carta;
@override final  String testo;

/// Create a copy of CartaOggi
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CartaOggiCopyWith<_CartaOggi> get copyWith => __$CartaOggiCopyWithImpl<_CartaOggi>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CartaOggiToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _CartaOggi&&(identical(other.giorno, giorno) || other.giorno == giorno)&&(identical(other.carta, carta) || other.carta == carta)&&(identical(other.testo, testo) || other.testo == testo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,giorno,carta,testo);
}

@override
String toString() {
    return 'CartaOggi(giorno: $giorno, carta: $carta, testo: $testo)';
}


}

/// @nodoc
abstract mixin class _$CartaOggiCopyWith<$Res> implements $CartaOggiCopyWith<$Res> {
  factory _$CartaOggiCopyWith(_CartaOggi value, $Res Function(_CartaOggi) _then) = __$CartaOggiCopyWithImpl;
@override @useResult
$Res call({
 String giorno, Carta carta, String testo
});


@override $CartaCopyWith<$Res> get carta;

}
/// @nodoc
class __$CartaOggiCopyWithImpl<$Res>
    implements _$CartaOggiCopyWith<$Res> {
  __$CartaOggiCopyWithImpl(this._self, this._then);

  final _CartaOggi _self;
  final $Res Function(_CartaOggi) _then;

/// Create a copy of CartaOggi
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? giorno = null,Object? carta = null,Object? testo = null,}) {
  return _then(_CartaOggi(
giorno: null == giorno ? _self.giorno : giorno // ignore: cast_nullable_to_non_nullable
as String,carta: null == carta ? _self.carta : carta // ignore: cast_nullable_to_non_nullable
as Carta,testo: null == testo ? _self.testo : testo // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

/// Create a copy of CartaOggi
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CartaCopyWith<$Res> get carta {
  
  return $CartaCopyWith<$Res>(_self.carta, (value) {
    return _then(_self.copyWith(carta: value));
  });
}
}


/// @nodoc
mixin _$CartaDelGiorno {

 String get giorno; Carta get carta; bool get rovescio; String get testo; int get serie;
/// Create a copy of CartaDelGiorno
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CartaDelGiornoCopyWith<CartaDelGiorno> get copyWith => _$CartaDelGiornoCopyWithImpl<CartaDelGiorno>(this as CartaDelGiorno, _$identity);

  /// Serializes this CartaDelGiorno to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as CartaDelGiorno;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CartaDelGiorno&&(identical(other.giorno, _this.giorno) || other.giorno == _this.giorno)&&(identical(other.carta, _this.carta) || other.carta == _this.carta)&&(identical(other.rovescio, _this.rovescio) || other.rovescio == _this.rovescio)&&(identical(other.testo, _this.testo) || other.testo == _this.testo)&&(identical(other.serie, _this.serie) || other.serie == _this.serie));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as CartaDelGiorno;
  return Object.hash(runtimeType,_this.giorno,_this.carta,_this.rovescio,_this.testo,_this.serie);
}

@override
String toString() {
  final _this = this as CartaDelGiorno;
  return 'CartaDelGiorno(giorno: ${_this.giorno}, carta: ${_this.carta}, rovescio: ${_this.rovescio}, testo: ${_this.testo}, serie: ${_this.serie})';
}


}

/// @nodoc
abstract mixin class $CartaDelGiornoCopyWith<$Res>  {
  factory $CartaDelGiornoCopyWith(CartaDelGiorno value, $Res Function(CartaDelGiorno) _then) = _$CartaDelGiornoCopyWithImpl;
@useResult
$Res call({
 String giorno, Carta carta, bool rovescio, String testo, int serie
});


$CartaCopyWith<$Res> get carta;

}
/// @nodoc
class _$CartaDelGiornoCopyWithImpl<$Res>
    implements $CartaDelGiornoCopyWith<$Res> {
  _$CartaDelGiornoCopyWithImpl(this._self, this._then);

  final CartaDelGiorno _self;
  final $Res Function(CartaDelGiorno) _then;

/// Create a copy of CartaDelGiorno
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? giorno = null,Object? carta = null,Object? rovescio = null,Object? testo = null,Object? serie = null,}) {
  return _then(CartaDelGiorno(
giorno: null == giorno ? _self.giorno : giorno // ignore: cast_nullable_to_non_nullable
as String,carta: null == carta ? _self.carta : carta // ignore: cast_nullable_to_non_nullable
as Carta,rovescio: null == rovescio ? _self.rovescio : rovescio // ignore: cast_nullable_to_non_nullable
as bool,testo: null == testo ? _self.testo : testo // ignore: cast_nullable_to_non_nullable
as String,serie: null == serie ? _self.serie : serie // ignore: cast_nullable_to_non_nullable
as int,
  ));
}
/// Create a copy of CartaDelGiorno
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CartaCopyWith<$Res> get carta {
  
  return $CartaCopyWith<$Res>(_self.carta, (value) {
    return _then(_self.copyWith(carta: value));
  });
}
}


/// Adds pattern-matching-related methods to [CartaDelGiorno].
extension CartaDelGiornoPatterns on CartaDelGiorno {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CartaDelGiorno value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CartaDelGiorno() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CartaDelGiorno value)  $default,){
final _that = this;
switch (_that) {
case _CartaDelGiorno():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CartaDelGiorno value)?  $default,){
final _that = this;
switch (_that) {
case _CartaDelGiorno() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String giorno,  Carta carta,  bool rovescio,  String testo,  int serie)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CartaDelGiorno() when $default != null:
return $default(_that.giorno,_that.carta,_that.rovescio,_that.testo,_that.serie);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String giorno,  Carta carta,  bool rovescio,  String testo,  int serie)  $default,) {final _that = this;
switch (_that) {
case _CartaDelGiorno():
return $default(_that.giorno,_that.carta,_that.rovescio,_that.testo,_that.serie);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String giorno,  Carta carta,  bool rovescio,  String testo,  int serie)?  $default,) {final _that = this;
switch (_that) {
case _CartaDelGiorno() when $default != null:
return $default(_that.giorno,_that.carta,_that.rovescio,_that.testo,_that.serie);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CartaDelGiorno implements CartaDelGiorno {
  const _CartaDelGiorno({required this.giorno, required this.carta, required this.rovescio, required this.testo, required this.serie});
  factory _CartaDelGiorno.fromJson(Map<String, dynamic> json) => _$CartaDelGiornoFromJson(json);

@override final  String giorno;
@override final  Carta carta;
@override final  bool rovescio;
@override final  String testo;
@override final  int serie;

/// Create a copy of CartaDelGiorno
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CartaDelGiornoCopyWith<_CartaDelGiorno> get copyWith => __$CartaDelGiornoCopyWithImpl<_CartaDelGiorno>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CartaDelGiornoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _CartaDelGiorno&&(identical(other.giorno, giorno) || other.giorno == giorno)&&(identical(other.carta, carta) || other.carta == carta)&&(identical(other.rovescio, rovescio) || other.rovescio == rovescio)&&(identical(other.testo, testo) || other.testo == testo)&&(identical(other.serie, serie) || other.serie == serie));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,giorno,carta,rovescio,testo,serie);
}

@override
String toString() {
    return 'CartaDelGiorno(giorno: $giorno, carta: $carta, rovescio: $rovescio, testo: $testo, serie: $serie)';
}


}

/// @nodoc
abstract mixin class _$CartaDelGiornoCopyWith<$Res> implements $CartaDelGiornoCopyWith<$Res> {
  factory _$CartaDelGiornoCopyWith(_CartaDelGiorno value, $Res Function(_CartaDelGiorno) _then) = __$CartaDelGiornoCopyWithImpl;
@override @useResult
$Res call({
 String giorno, Carta carta, bool rovescio, String testo, int serie
});


@override $CartaCopyWith<$Res> get carta;

}
/// @nodoc
class __$CartaDelGiornoCopyWithImpl<$Res>
    implements _$CartaDelGiornoCopyWith<$Res> {
  __$CartaDelGiornoCopyWithImpl(this._self, this._then);

  final _CartaDelGiorno _self;
  final $Res Function(_CartaDelGiorno) _then;

/// Create a copy of CartaDelGiorno
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? giorno = null,Object? carta = null,Object? rovescio = null,Object? testo = null,Object? serie = null,}) {
  return _then(_CartaDelGiorno(
giorno: null == giorno ? _self.giorno : giorno // ignore: cast_nullable_to_non_nullable
as String,carta: null == carta ? _self.carta : carta // ignore: cast_nullable_to_non_nullable
as Carta,rovescio: null == rovescio ? _self.rovescio : rovescio // ignore: cast_nullable_to_non_nullable
as bool,testo: null == testo ? _self.testo : testo // ignore: cast_nullable_to_non_nullable
as String,serie: null == serie ? _self.serie : serie // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

/// Create a copy of CartaDelGiorno
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CartaCopyWith<$Res> get carta {
  
  return $CartaCopyWith<$Res>(_self.carta, (value) {
    return _then(_self.copyWith(carta: value));
  });
}
}


/// @nodoc
mixin _$ImpostazioniPubbliche {

 int get creditiIscrizione; int get creditiInvito; num get commissioneReferralPercentuale;/// v9.5: quante persone su cento ricevono la lettura in chat (prova 90/10, dalla console).
 int get letturaChatPercentuale;/// Il minimo di domande dell'intervista: a zero si può saltarla («Invia quesito e inizia a mescolare le carte»).
 int get intervistaMinDomande;
/// Create a copy of ImpostazioniPubbliche
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ImpostazioniPubblicheCopyWith<ImpostazioniPubbliche> get copyWith => _$ImpostazioniPubblicheCopyWithImpl<ImpostazioniPubbliche>(this as ImpostazioniPubbliche, _$identity);

  /// Serializes this ImpostazioniPubbliche to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as ImpostazioniPubbliche;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ImpostazioniPubbliche&&(identical(other.creditiIscrizione, _this.creditiIscrizione) || other.creditiIscrizione == _this.creditiIscrizione)&&(identical(other.creditiInvito, _this.creditiInvito) || other.creditiInvito == _this.creditiInvito)&&(identical(other.commissioneReferralPercentuale, _this.commissioneReferralPercentuale) || other.commissioneReferralPercentuale == _this.commissioneReferralPercentuale)&&(identical(other.letturaChatPercentuale, _this.letturaChatPercentuale) || other.letturaChatPercentuale == _this.letturaChatPercentuale)&&(identical(other.intervistaMinDomande, _this.intervistaMinDomande) || other.intervistaMinDomande == _this.intervistaMinDomande));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as ImpostazioniPubbliche;
  return Object.hash(runtimeType,_this.creditiIscrizione,_this.creditiInvito,_this.commissioneReferralPercentuale,_this.letturaChatPercentuale,_this.intervistaMinDomande);
}

@override
String toString() {
  final _this = this as ImpostazioniPubbliche;
  return 'ImpostazioniPubbliche(creditiIscrizione: ${_this.creditiIscrizione}, creditiInvito: ${_this.creditiInvito}, commissioneReferralPercentuale: ${_this.commissioneReferralPercentuale}, letturaChatPercentuale: ${_this.letturaChatPercentuale}, intervistaMinDomande: ${_this.intervistaMinDomande})';
}


}

/// @nodoc
abstract mixin class $ImpostazioniPubblicheCopyWith<$Res>  {
  factory $ImpostazioniPubblicheCopyWith(ImpostazioniPubbliche value, $Res Function(ImpostazioniPubbliche) _then) = _$ImpostazioniPubblicheCopyWithImpl;
@useResult
$Res call({
 int creditiIscrizione, int creditiInvito, num commissioneReferralPercentuale, int letturaChatPercentuale, int intervistaMinDomande
});




}
/// @nodoc
class _$ImpostazioniPubblicheCopyWithImpl<$Res>
    implements $ImpostazioniPubblicheCopyWith<$Res> {
  _$ImpostazioniPubblicheCopyWithImpl(this._self, this._then);

  final ImpostazioniPubbliche _self;
  final $Res Function(ImpostazioniPubbliche) _then;

/// Create a copy of ImpostazioniPubbliche
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? creditiIscrizione = null,Object? creditiInvito = null,Object? commissioneReferralPercentuale = null,Object? letturaChatPercentuale = null,Object? intervistaMinDomande = null,}) {
  return _then(ImpostazioniPubbliche(
creditiIscrizione: null == creditiIscrizione ? _self.creditiIscrizione : creditiIscrizione // ignore: cast_nullable_to_non_nullable
as int,creditiInvito: null == creditiInvito ? _self.creditiInvito : creditiInvito // ignore: cast_nullable_to_non_nullable
as int,commissioneReferralPercentuale: null == commissioneReferralPercentuale ? _self.commissioneReferralPercentuale : commissioneReferralPercentuale // ignore: cast_nullable_to_non_nullable
as num,letturaChatPercentuale: null == letturaChatPercentuale ? _self.letturaChatPercentuale : letturaChatPercentuale // ignore: cast_nullable_to_non_nullable
as int,intervistaMinDomande: null == intervistaMinDomande ? _self.intervistaMinDomande : intervistaMinDomande // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [ImpostazioniPubbliche].
extension ImpostazioniPubblichePatterns on ImpostazioniPubbliche {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ImpostazioniPubbliche value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ImpostazioniPubbliche() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ImpostazioniPubbliche value)  $default,){
final _that = this;
switch (_that) {
case _ImpostazioniPubbliche():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ImpostazioniPubbliche value)?  $default,){
final _that = this;
switch (_that) {
case _ImpostazioniPubbliche() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int creditiIscrizione,  int creditiInvito,  num commissioneReferralPercentuale,  int letturaChatPercentuale,  int intervistaMinDomande)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ImpostazioniPubbliche() when $default != null:
return $default(_that.creditiIscrizione,_that.creditiInvito,_that.commissioneReferralPercentuale,_that.letturaChatPercentuale,_that.intervistaMinDomande);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int creditiIscrizione,  int creditiInvito,  num commissioneReferralPercentuale,  int letturaChatPercentuale,  int intervistaMinDomande)  $default,) {final _that = this;
switch (_that) {
case _ImpostazioniPubbliche():
return $default(_that.creditiIscrizione,_that.creditiInvito,_that.commissioneReferralPercentuale,_that.letturaChatPercentuale,_that.intervistaMinDomande);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int creditiIscrizione,  int creditiInvito,  num commissioneReferralPercentuale,  int letturaChatPercentuale,  int intervistaMinDomande)?  $default,) {final _that = this;
switch (_that) {
case _ImpostazioniPubbliche() when $default != null:
return $default(_that.creditiIscrizione,_that.creditiInvito,_that.commissioneReferralPercentuale,_that.letturaChatPercentuale,_that.intervistaMinDomande);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ImpostazioniPubbliche implements ImpostazioniPubbliche {
  const _ImpostazioniPubbliche({required this.creditiIscrizione, required this.creditiInvito, this.commissioneReferralPercentuale = 0, this.letturaChatPercentuale = 90, this.intervistaMinDomande = 0});
  factory _ImpostazioniPubbliche.fromJson(Map<String, dynamic> json) => _$ImpostazioniPubblicheFromJson(json);

@override final  int creditiIscrizione;
@override final  int creditiInvito;
@override@JsonKey() final  num commissioneReferralPercentuale;
/// v9.5: quante persone su cento ricevono la lettura in chat (prova 90/10, dalla console).
@override@JsonKey() final  int letturaChatPercentuale;
/// Il minimo di domande dell'intervista: a zero si può saltarla («Invia quesito e inizia a mescolare le carte»).
@override@JsonKey() final  int intervistaMinDomande;

/// Create a copy of ImpostazioniPubbliche
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ImpostazioniPubblicheCopyWith<_ImpostazioniPubbliche> get copyWith => __$ImpostazioniPubblicheCopyWithImpl<_ImpostazioniPubbliche>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ImpostazioniPubblicheToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _ImpostazioniPubbliche&&(identical(other.creditiIscrizione, creditiIscrizione) || other.creditiIscrizione == creditiIscrizione)&&(identical(other.creditiInvito, creditiInvito) || other.creditiInvito == creditiInvito)&&(identical(other.commissioneReferralPercentuale, commissioneReferralPercentuale) || other.commissioneReferralPercentuale == commissioneReferralPercentuale)&&(identical(other.letturaChatPercentuale, letturaChatPercentuale) || other.letturaChatPercentuale == letturaChatPercentuale)&&(identical(other.intervistaMinDomande, intervistaMinDomande) || other.intervistaMinDomande == intervistaMinDomande));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,creditiIscrizione,creditiInvito,commissioneReferralPercentuale,letturaChatPercentuale,intervistaMinDomande);
}

@override
String toString() {
    return 'ImpostazioniPubbliche(creditiIscrizione: $creditiIscrizione, creditiInvito: $creditiInvito, commissioneReferralPercentuale: $commissioneReferralPercentuale, letturaChatPercentuale: $letturaChatPercentuale, intervistaMinDomande: $intervistaMinDomande)';
}


}

/// @nodoc
abstract mixin class _$ImpostazioniPubblicheCopyWith<$Res> implements $ImpostazioniPubblicheCopyWith<$Res> {
  factory _$ImpostazioniPubblicheCopyWith(_ImpostazioniPubbliche value, $Res Function(_ImpostazioniPubbliche) _then) = __$ImpostazioniPubblicheCopyWithImpl;
@override @useResult
$Res call({
 int creditiIscrizione, int creditiInvito, num commissioneReferralPercentuale, int letturaChatPercentuale, int intervistaMinDomande
});




}
/// @nodoc
class __$ImpostazioniPubblicheCopyWithImpl<$Res>
    implements _$ImpostazioniPubblicheCopyWith<$Res> {
  __$ImpostazioniPubblicheCopyWithImpl(this._self, this._then);

  final _ImpostazioniPubbliche _self;
  final $Res Function(_ImpostazioniPubbliche) _then;

/// Create a copy of ImpostazioniPubbliche
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? creditiIscrizione = null,Object? creditiInvito = null,Object? commissioneReferralPercentuale = null,Object? letturaChatPercentuale = null,Object? intervistaMinDomande = null,}) {
  return _then(_ImpostazioniPubbliche(
creditiIscrizione: null == creditiIscrizione ? _self.creditiIscrizione : creditiIscrizione // ignore: cast_nullable_to_non_nullable
as int,creditiInvito: null == creditiInvito ? _self.creditiInvito : creditiInvito // ignore: cast_nullable_to_non_nullable
as int,commissioneReferralPercentuale: null == commissioneReferralPercentuale ? _self.commissioneReferralPercentuale : commissioneReferralPercentuale // ignore: cast_nullable_to_non_nullable
as num,letturaChatPercentuale: null == letturaChatPercentuale ? _self.letturaChatPercentuale : letturaChatPercentuale // ignore: cast_nullable_to_non_nullable
as int,intervistaMinDomande: null == intervistaMinDomande ? _self.intervistaMinDomande : intervistaMinDomande // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$EtaMinima {

 int get anni; String? get paese;
/// Create a copy of EtaMinima
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$EtaMinimaCopyWith<EtaMinima> get copyWith => _$EtaMinimaCopyWithImpl<EtaMinima>(this as EtaMinima, _$identity);

  /// Serializes this EtaMinima to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as EtaMinima;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is EtaMinima&&(identical(other.anni, _this.anni) || other.anni == _this.anni)&&(identical(other.paese, _this.paese) || other.paese == _this.paese));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as EtaMinima;
  return Object.hash(runtimeType,_this.anni,_this.paese);
}

@override
String toString() {
  final _this = this as EtaMinima;
  return 'EtaMinima(anni: ${_this.anni}, paese: ${_this.paese})';
}


}

/// @nodoc
abstract mixin class $EtaMinimaCopyWith<$Res>  {
  factory $EtaMinimaCopyWith(EtaMinima value, $Res Function(EtaMinima) _then) = _$EtaMinimaCopyWithImpl;
@useResult
$Res call({
 int anni, String? paese
});




}
/// @nodoc
class _$EtaMinimaCopyWithImpl<$Res>
    implements $EtaMinimaCopyWith<$Res> {
  _$EtaMinimaCopyWithImpl(this._self, this._then);

  final EtaMinima _self;
  final $Res Function(EtaMinima) _then;

/// Create a copy of EtaMinima
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? anni = null,Object? paese = freezed,}) {
  return _then(EtaMinima(
anni: null == anni ? _self.anni : anni // ignore: cast_nullable_to_non_nullable
as int,paese: freezed == paese ? _self.paese : paese // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [EtaMinima].
extension EtaMinimaPatterns on EtaMinima {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _EtaMinima value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _EtaMinima() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _EtaMinima value)  $default,){
final _that = this;
switch (_that) {
case _EtaMinima():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _EtaMinima value)?  $default,){
final _that = this;
switch (_that) {
case _EtaMinima() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int anni,  String? paese)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _EtaMinima() when $default != null:
return $default(_that.anni,_that.paese);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int anni,  String? paese)  $default,) {final _that = this;
switch (_that) {
case _EtaMinima():
return $default(_that.anni,_that.paese);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int anni,  String? paese)?  $default,) {final _that = this;
switch (_that) {
case _EtaMinima() when $default != null:
return $default(_that.anni,_that.paese);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _EtaMinima implements EtaMinima {
  const _EtaMinima({required this.anni, this.paese});
  factory _EtaMinima.fromJson(Map<String, dynamic> json) => _$EtaMinimaFromJson(json);

@override final  int anni;
@override final  String? paese;

/// Create a copy of EtaMinima
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$EtaMinimaCopyWith<_EtaMinima> get copyWith => __$EtaMinimaCopyWithImpl<_EtaMinima>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$EtaMinimaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _EtaMinima&&(identical(other.anni, anni) || other.anni == anni)&&(identical(other.paese, paese) || other.paese == paese));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,anni,paese);
}

@override
String toString() {
    return 'EtaMinima(anni: $anni, paese: $paese)';
}


}

/// @nodoc
abstract mixin class _$EtaMinimaCopyWith<$Res> implements $EtaMinimaCopyWith<$Res> {
  factory _$EtaMinimaCopyWith(_EtaMinima value, $Res Function(_EtaMinima) _then) = __$EtaMinimaCopyWithImpl;
@override @useResult
$Res call({
 int anni, String? paese
});




}
/// @nodoc
class __$EtaMinimaCopyWithImpl<$Res>
    implements _$EtaMinimaCopyWith<$Res> {
  __$EtaMinimaCopyWithImpl(this._self, this._then);

  final _EtaMinima _self;
  final $Res Function(_EtaMinima) _then;

/// Create a copy of EtaMinima
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? anni = null,Object? paese = freezed,}) {
  return _then(_EtaMinima(
anni: null == anni ? _self.anni : anni // ignore: cast_nullable_to_non_nullable
as int,paese: freezed == paese ? _self.paese : paese // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$ImmagineArticolo {

 String? get url; String? get mini; String? get alt; int? get larghezza; int? get altezza;
/// Create a copy of ImmagineArticolo
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ImmagineArticoloCopyWith<ImmagineArticolo> get copyWith => _$ImmagineArticoloCopyWithImpl<ImmagineArticolo>(this as ImmagineArticolo, _$identity);

  /// Serializes this ImmagineArticolo to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as ImmagineArticolo;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ImmagineArticolo&&(identical(other.url, _this.url) || other.url == _this.url)&&(identical(other.mini, _this.mini) || other.mini == _this.mini)&&(identical(other.alt, _this.alt) || other.alt == _this.alt)&&(identical(other.larghezza, _this.larghezza) || other.larghezza == _this.larghezza)&&(identical(other.altezza, _this.altezza) || other.altezza == _this.altezza));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as ImmagineArticolo;
  return Object.hash(runtimeType,_this.url,_this.mini,_this.alt,_this.larghezza,_this.altezza);
}

@override
String toString() {
  final _this = this as ImmagineArticolo;
  return 'ImmagineArticolo(url: ${_this.url}, mini: ${_this.mini}, alt: ${_this.alt}, larghezza: ${_this.larghezza}, altezza: ${_this.altezza})';
}


}

/// @nodoc
abstract mixin class $ImmagineArticoloCopyWith<$Res>  {
  factory $ImmagineArticoloCopyWith(ImmagineArticolo value, $Res Function(ImmagineArticolo) _then) = _$ImmagineArticoloCopyWithImpl;
@useResult
$Res call({
 String? url, String? mini, String? alt, int? larghezza, int? altezza
});




}
/// @nodoc
class _$ImmagineArticoloCopyWithImpl<$Res>
    implements $ImmagineArticoloCopyWith<$Res> {
  _$ImmagineArticoloCopyWithImpl(this._self, this._then);

  final ImmagineArticolo _self;
  final $Res Function(ImmagineArticolo) _then;

/// Create a copy of ImmagineArticolo
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? url = freezed,Object? mini = freezed,Object? alt = freezed,Object? larghezza = freezed,Object? altezza = freezed,}) {
  return _then(ImmagineArticolo(
url: freezed == url ? _self.url : url // ignore: cast_nullable_to_non_nullable
as String?,mini: freezed == mini ? _self.mini : mini // ignore: cast_nullable_to_non_nullable
as String?,alt: freezed == alt ? _self.alt : alt // ignore: cast_nullable_to_non_nullable
as String?,larghezza: freezed == larghezza ? _self.larghezza : larghezza // ignore: cast_nullable_to_non_nullable
as int?,altezza: freezed == altezza ? _self.altezza : altezza // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}

}


/// Adds pattern-matching-related methods to [ImmagineArticolo].
extension ImmagineArticoloPatterns on ImmagineArticolo {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ImmagineArticolo value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ImmagineArticolo() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ImmagineArticolo value)  $default,){
final _that = this;
switch (_that) {
case _ImmagineArticolo():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ImmagineArticolo value)?  $default,){
final _that = this;
switch (_that) {
case _ImmagineArticolo() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? url,  String? mini,  String? alt,  int? larghezza,  int? altezza)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ImmagineArticolo() when $default != null:
return $default(_that.url,_that.mini,_that.alt,_that.larghezza,_that.altezza);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? url,  String? mini,  String? alt,  int? larghezza,  int? altezza)  $default,) {final _that = this;
switch (_that) {
case _ImmagineArticolo():
return $default(_that.url,_that.mini,_that.alt,_that.larghezza,_that.altezza);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? url,  String? mini,  String? alt,  int? larghezza,  int? altezza)?  $default,) {final _that = this;
switch (_that) {
case _ImmagineArticolo() when $default != null:
return $default(_that.url,_that.mini,_that.alt,_that.larghezza,_that.altezza);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ImmagineArticolo implements ImmagineArticolo {
  const _ImmagineArticolo({this.url, this.mini, this.alt, this.larghezza, this.altezza});
  factory _ImmagineArticolo.fromJson(Map<String, dynamic> json) => _$ImmagineArticoloFromJson(json);

@override final  String? url;
@override final  String? mini;
@override final  String? alt;
@override final  int? larghezza;
@override final  int? altezza;

/// Create a copy of ImmagineArticolo
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ImmagineArticoloCopyWith<_ImmagineArticolo> get copyWith => __$ImmagineArticoloCopyWithImpl<_ImmagineArticolo>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ImmagineArticoloToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _ImmagineArticolo&&(identical(other.url, url) || other.url == url)&&(identical(other.mini, mini) || other.mini == mini)&&(identical(other.alt, alt) || other.alt == alt)&&(identical(other.larghezza, larghezza) || other.larghezza == larghezza)&&(identical(other.altezza, altezza) || other.altezza == altezza));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,url,mini,alt,larghezza,altezza);
}

@override
String toString() {
    return 'ImmagineArticolo(url: $url, mini: $mini, alt: $alt, larghezza: $larghezza, altezza: $altezza)';
}


}

/// @nodoc
abstract mixin class _$ImmagineArticoloCopyWith<$Res> implements $ImmagineArticoloCopyWith<$Res> {
  factory _$ImmagineArticoloCopyWith(_ImmagineArticolo value, $Res Function(_ImmagineArticolo) _then) = __$ImmagineArticoloCopyWithImpl;
@override @useResult
$Res call({
 String? url, String? mini, String? alt, int? larghezza, int? altezza
});




}
/// @nodoc
class __$ImmagineArticoloCopyWithImpl<$Res>
    implements _$ImmagineArticoloCopyWith<$Res> {
  __$ImmagineArticoloCopyWithImpl(this._self, this._then);

  final _ImmagineArticolo _self;
  final $Res Function(_ImmagineArticolo) _then;

/// Create a copy of ImmagineArticolo
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? url = freezed,Object? mini = freezed,Object? alt = freezed,Object? larghezza = freezed,Object? altezza = freezed,}) {
  return _then(_ImmagineArticolo(
url: freezed == url ? _self.url : url // ignore: cast_nullable_to_non_nullable
as String?,mini: freezed == mini ? _self.mini : mini // ignore: cast_nullable_to_non_nullable
as String?,alt: freezed == alt ? _self.alt : alt // ignore: cast_nullable_to_non_nullable
as String?,larghezza: freezed == larghezza ? _self.larghezza : larghezza // ignore: cast_nullable_to_non_nullable
as int?,altezza: freezed == altezza ? _self.altezza : altezza // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}


}


/// @nodoc
mixin _$Voce {

 String get slug; String get nome;
/// Create a copy of Voce
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$VoceCopyWith<Voce> get copyWith => _$VoceCopyWithImpl<Voce>(this as Voce, _$identity);

  /// Serializes this Voce to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Voce;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Voce&&(identical(other.slug, _this.slug) || other.slug == _this.slug)&&(identical(other.nome, _this.nome) || other.nome == _this.nome));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Voce;
  return Object.hash(runtimeType,_this.slug,_this.nome);
}

@override
String toString() {
  final _this = this as Voce;
  return 'Voce(slug: ${_this.slug}, nome: ${_this.nome})';
}


}

/// @nodoc
abstract mixin class $VoceCopyWith<$Res>  {
  factory $VoceCopyWith(Voce value, $Res Function(Voce) _then) = _$VoceCopyWithImpl;
@useResult
$Res call({
 String slug, String nome
});




}
/// @nodoc
class _$VoceCopyWithImpl<$Res>
    implements $VoceCopyWith<$Res> {
  _$VoceCopyWithImpl(this._self, this._then);

  final Voce _self;
  final $Res Function(Voce) _then;

/// Create a copy of Voce
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? slug = null,Object? nome = null,}) {
  return _then(Voce(
slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [Voce].
extension VocePatterns on Voce {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Voce value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Voce() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Voce value)  $default,){
final _that = this;
switch (_that) {
case _Voce():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Voce value)?  $default,){
final _that = this;
switch (_that) {
case _Voce() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String slug,  String nome)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Voce() when $default != null:
return $default(_that.slug,_that.nome);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String slug,  String nome)  $default,) {final _that = this;
switch (_that) {
case _Voce():
return $default(_that.slug,_that.nome);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String slug,  String nome)?  $default,) {final _that = this;
switch (_that) {
case _Voce() when $default != null:
return $default(_that.slug,_that.nome);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Voce implements Voce {
  const _Voce({required this.slug, required this.nome});
  factory _Voce.fromJson(Map<String, dynamic> json) => _$VoceFromJson(json);

@override final  String slug;
@override final  String nome;

/// Create a copy of Voce
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$VoceCopyWith<_Voce> get copyWith => __$VoceCopyWithImpl<_Voce>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$VoceToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Voce&&(identical(other.slug, slug) || other.slug == slug)&&(identical(other.nome, nome) || other.nome == nome));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,slug,nome);
}

@override
String toString() {
    return 'Voce(slug: $slug, nome: $nome)';
}


}

/// @nodoc
abstract mixin class _$VoceCopyWith<$Res> implements $VoceCopyWith<$Res> {
  factory _$VoceCopyWith(_Voce value, $Res Function(_Voce) _then) = __$VoceCopyWithImpl;
@override @useResult
$Res call({
 String slug, String nome
});




}
/// @nodoc
class __$VoceCopyWithImpl<$Res>
    implements _$VoceCopyWith<$Res> {
  __$VoceCopyWithImpl(this._self, this._then);

  final _Voce _self;
  final $Res Function(_Voce) _then;

/// Create a copy of Voce
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? slug = null,Object? nome = null,}) {
  return _then(_Voce(
slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$AutoreBlog {

 int? get id; String get nome; String? get avatar;
/// Create a copy of AutoreBlog
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AutoreBlogCopyWith<AutoreBlog> get copyWith => _$AutoreBlogCopyWithImpl<AutoreBlog>(this as AutoreBlog, _$identity);

  /// Serializes this AutoreBlog to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as AutoreBlog;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AutoreBlog&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.avatar, _this.avatar) || other.avatar == _this.avatar));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as AutoreBlog;
  return Object.hash(runtimeType,_this.id,_this.nome,_this.avatar);
}

@override
String toString() {
  final _this = this as AutoreBlog;
  return 'AutoreBlog(id: ${_this.id}, nome: ${_this.nome}, avatar: ${_this.avatar})';
}


}

/// @nodoc
abstract mixin class $AutoreBlogCopyWith<$Res>  {
  factory $AutoreBlogCopyWith(AutoreBlog value, $Res Function(AutoreBlog) _then) = _$AutoreBlogCopyWithImpl;
@useResult
$Res call({
 int? id, String nome, String? avatar
});




}
/// @nodoc
class _$AutoreBlogCopyWithImpl<$Res>
    implements $AutoreBlogCopyWith<$Res> {
  _$AutoreBlogCopyWithImpl(this._self, this._then);

  final AutoreBlog _self;
  final $Res Function(AutoreBlog) _then;

/// Create a copy of AutoreBlog
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = freezed,Object? nome = null,Object? avatar = freezed,}) {
  return _then(AutoreBlog(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int?,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,avatar: freezed == avatar ? _self.avatar : avatar // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [AutoreBlog].
extension AutoreBlogPatterns on AutoreBlog {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _AutoreBlog value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _AutoreBlog() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _AutoreBlog value)  $default,){
final _that = this;
switch (_that) {
case _AutoreBlog():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _AutoreBlog value)?  $default,){
final _that = this;
switch (_that) {
case _AutoreBlog() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int? id,  String nome,  String? avatar)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _AutoreBlog() when $default != null:
return $default(_that.id,_that.nome,_that.avatar);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int? id,  String nome,  String? avatar)  $default,) {final _that = this;
switch (_that) {
case _AutoreBlog():
return $default(_that.id,_that.nome,_that.avatar);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int? id,  String nome,  String? avatar)?  $default,) {final _that = this;
switch (_that) {
case _AutoreBlog() when $default != null:
return $default(_that.id,_that.nome,_that.avatar);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _AutoreBlog implements AutoreBlog {
  const _AutoreBlog({this.id, required this.nome, this.avatar});
  factory _AutoreBlog.fromJson(Map<String, dynamic> json) => _$AutoreBlogFromJson(json);

@override final  int? id;
@override final  String nome;
@override final  String? avatar;

/// Create a copy of AutoreBlog
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$AutoreBlogCopyWith<_AutoreBlog> get copyWith => __$AutoreBlogCopyWithImpl<_AutoreBlog>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$AutoreBlogToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _AutoreBlog&&(identical(other.id, id) || other.id == id)&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.avatar, avatar) || other.avatar == avatar));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,nome,avatar);
}

@override
String toString() {
    return 'AutoreBlog(id: $id, nome: $nome, avatar: $avatar)';
}


}

/// @nodoc
abstract mixin class _$AutoreBlogCopyWith<$Res> implements $AutoreBlogCopyWith<$Res> {
  factory _$AutoreBlogCopyWith(_AutoreBlog value, $Res Function(_AutoreBlog) _then) = __$AutoreBlogCopyWithImpl;
@override @useResult
$Res call({
 int? id, String nome, String? avatar
});




}
/// @nodoc
class __$AutoreBlogCopyWithImpl<$Res>
    implements _$AutoreBlogCopyWith<$Res> {
  __$AutoreBlogCopyWithImpl(this._self, this._then);

  final _AutoreBlog _self;
  final $Res Function(_AutoreBlog) _then;

/// Create a copy of AutoreBlog
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? nome = null,Object? avatar = freezed,}) {
  return _then(_AutoreBlog(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int?,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,avatar: freezed == avatar ? _self.avatar : avatar // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$SoggettoArticolo {

 String get tipo; String get ref; String? get nome; String? get slug;
/// Create a copy of SoggettoArticolo
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SoggettoArticoloCopyWith<SoggettoArticolo> get copyWith => _$SoggettoArticoloCopyWithImpl<SoggettoArticolo>(this as SoggettoArticolo, _$identity);

  /// Serializes this SoggettoArticolo to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as SoggettoArticolo;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SoggettoArticolo&&(identical(other.tipo, _this.tipo) || other.tipo == _this.tipo)&&(identical(other.ref, _this.ref) || other.ref == _this.ref)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.slug, _this.slug) || other.slug == _this.slug));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as SoggettoArticolo;
  return Object.hash(runtimeType,_this.tipo,_this.ref,_this.nome,_this.slug);
}

@override
String toString() {
  final _this = this as SoggettoArticolo;
  return 'SoggettoArticolo(tipo: ${_this.tipo}, ref: ${_this.ref}, nome: ${_this.nome}, slug: ${_this.slug})';
}


}

/// @nodoc
abstract mixin class $SoggettoArticoloCopyWith<$Res>  {
  factory $SoggettoArticoloCopyWith(SoggettoArticolo value, $Res Function(SoggettoArticolo) _then) = _$SoggettoArticoloCopyWithImpl;
@useResult
$Res call({
 String tipo, String ref, String? nome, String? slug
});




}
/// @nodoc
class _$SoggettoArticoloCopyWithImpl<$Res>
    implements $SoggettoArticoloCopyWith<$Res> {
  _$SoggettoArticoloCopyWithImpl(this._self, this._then);

  final SoggettoArticolo _self;
  final $Res Function(SoggettoArticolo) _then;

/// Create a copy of SoggettoArticolo
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? tipo = null,Object? ref = null,Object? nome = freezed,Object? slug = freezed,}) {
  return _then(SoggettoArticolo(
tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,ref: null == ref ? _self.ref : ref // ignore: cast_nullable_to_non_nullable
as String,nome: freezed == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String?,slug: freezed == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [SoggettoArticolo].
extension SoggettoArticoloPatterns on SoggettoArticolo {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _SoggettoArticolo value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _SoggettoArticolo() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _SoggettoArticolo value)  $default,){
final _that = this;
switch (_that) {
case _SoggettoArticolo():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _SoggettoArticolo value)?  $default,){
final _that = this;
switch (_that) {
case _SoggettoArticolo() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String tipo,  String ref,  String? nome,  String? slug)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _SoggettoArticolo() when $default != null:
return $default(_that.tipo,_that.ref,_that.nome,_that.slug);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String tipo,  String ref,  String? nome,  String? slug)  $default,) {final _that = this;
switch (_that) {
case _SoggettoArticolo():
return $default(_that.tipo,_that.ref,_that.nome,_that.slug);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String tipo,  String ref,  String? nome,  String? slug)?  $default,) {final _that = this;
switch (_that) {
case _SoggettoArticolo() when $default != null:
return $default(_that.tipo,_that.ref,_that.nome,_that.slug);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _SoggettoArticolo implements SoggettoArticolo {
  const _SoggettoArticolo({required this.tipo, required this.ref, this.nome, this.slug});
  factory _SoggettoArticolo.fromJson(Map<String, dynamic> json) => _$SoggettoArticoloFromJson(json);

@override final  String tipo;
@override final  String ref;
@override final  String? nome;
@override final  String? slug;

/// Create a copy of SoggettoArticolo
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SoggettoArticoloCopyWith<_SoggettoArticolo> get copyWith => __$SoggettoArticoloCopyWithImpl<_SoggettoArticolo>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SoggettoArticoloToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _SoggettoArticolo&&(identical(other.tipo, tipo) || other.tipo == tipo)&&(identical(other.ref, ref) || other.ref == ref)&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.slug, slug) || other.slug == slug));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,tipo,ref,nome,slug);
}

@override
String toString() {
    return 'SoggettoArticolo(tipo: $tipo, ref: $ref, nome: $nome, slug: $slug)';
}


}

/// @nodoc
abstract mixin class _$SoggettoArticoloCopyWith<$Res> implements $SoggettoArticoloCopyWith<$Res> {
  factory _$SoggettoArticoloCopyWith(_SoggettoArticolo value, $Res Function(_SoggettoArticolo) _then) = __$SoggettoArticoloCopyWithImpl;
@override @useResult
$Res call({
 String tipo, String ref, String? nome, String? slug
});




}
/// @nodoc
class __$SoggettoArticoloCopyWithImpl<$Res>
    implements _$SoggettoArticoloCopyWith<$Res> {
  __$SoggettoArticoloCopyWithImpl(this._self, this._then);

  final _SoggettoArticolo _self;
  final $Res Function(_SoggettoArticolo) _then;

/// Create a copy of SoggettoArticolo
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? tipo = null,Object? ref = null,Object? nome = freezed,Object? slug = freezed,}) {
  return _then(_SoggettoArticolo(
tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,ref: null == ref ? _self.ref : ref // ignore: cast_nullable_to_non_nullable
as String,nome: freezed == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String?,slug: freezed == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$ArticoloBreve {

 String get slug; String get titolo; String? get sottotitolo; String? get estratto; ImmagineArticolo? get immagine; Voce? get sezione; int get tempoLettura; List<Voce> get tags; String? get lang; AutoreBlog? get autore; String? get pubblicatoIl; String? get aggiornatoIl; bool get inEvidenza;/// La carta o la stesa di cui parla (v9.4), o null.
 SoggettoArticolo? get soggetto;
/// Create a copy of ArticoloBreve
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ArticoloBreveCopyWith<ArticoloBreve> get copyWith => _$ArticoloBreveCopyWithImpl<ArticoloBreve>(this as ArticoloBreve, _$identity);

  /// Serializes this ArticoloBreve to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as ArticoloBreve;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ArticoloBreve&&(identical(other.slug, _this.slug) || other.slug == _this.slug)&&(identical(other.titolo, _this.titolo) || other.titolo == _this.titolo)&&(identical(other.sottotitolo, _this.sottotitolo) || other.sottotitolo == _this.sottotitolo)&&(identical(other.estratto, _this.estratto) || other.estratto == _this.estratto)&&(identical(other.immagine, _this.immagine) || other.immagine == _this.immagine)&&(identical(other.sezione, _this.sezione) || other.sezione == _this.sezione)&&(identical(other.tempoLettura, _this.tempoLettura) || other.tempoLettura == _this.tempoLettura)&&const DeepCollectionEquality().equals(other.tags, _this.tags)&&(identical(other.lang, _this.lang) || other.lang == _this.lang)&&(identical(other.autore, _this.autore) || other.autore == _this.autore)&&(identical(other.pubblicatoIl, _this.pubblicatoIl) || other.pubblicatoIl == _this.pubblicatoIl)&&(identical(other.aggiornatoIl, _this.aggiornatoIl) || other.aggiornatoIl == _this.aggiornatoIl)&&(identical(other.inEvidenza, _this.inEvidenza) || other.inEvidenza == _this.inEvidenza)&&(identical(other.soggetto, _this.soggetto) || other.soggetto == _this.soggetto));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as ArticoloBreve;
  return Object.hash(runtimeType,_this.slug,_this.titolo,_this.sottotitolo,_this.estratto,_this.immagine,_this.sezione,_this.tempoLettura,const DeepCollectionEquality().hash(_this.tags),_this.lang,_this.autore,_this.pubblicatoIl,_this.aggiornatoIl,_this.inEvidenza,_this.soggetto);
}

@override
String toString() {
  final _this = this as ArticoloBreve;
  return 'ArticoloBreve(slug: ${_this.slug}, titolo: ${_this.titolo}, sottotitolo: ${_this.sottotitolo}, estratto: ${_this.estratto}, immagine: ${_this.immagine}, sezione: ${_this.sezione}, tempoLettura: ${_this.tempoLettura}, tags: ${_this.tags}, lang: ${_this.lang}, autore: ${_this.autore}, pubblicatoIl: ${_this.pubblicatoIl}, aggiornatoIl: ${_this.aggiornatoIl}, inEvidenza: ${_this.inEvidenza}, soggetto: ${_this.soggetto})';
}


}

/// @nodoc
abstract mixin class $ArticoloBreveCopyWith<$Res>  {
  factory $ArticoloBreveCopyWith(ArticoloBreve value, $Res Function(ArticoloBreve) _then) = _$ArticoloBreveCopyWithImpl;
@useResult
$Res call({
 String slug, String titolo, String? sottotitolo, String? estratto, ImmagineArticolo? immagine, Voce? sezione, int tempoLettura, List<Voce> tags, String? lang, AutoreBlog? autore, String? pubblicatoIl, String? aggiornatoIl, bool inEvidenza, SoggettoArticolo? soggetto
});


$ImmagineArticoloCopyWith<$Res>? get immagine;$VoceCopyWith<$Res>? get sezione;$AutoreBlogCopyWith<$Res>? get autore;$SoggettoArticoloCopyWith<$Res>? get soggetto;

}
/// @nodoc
class _$ArticoloBreveCopyWithImpl<$Res>
    implements $ArticoloBreveCopyWith<$Res> {
  _$ArticoloBreveCopyWithImpl(this._self, this._then);

  final ArticoloBreve _self;
  final $Res Function(ArticoloBreve) _then;

/// Create a copy of ArticoloBreve
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? slug = null,Object? titolo = null,Object? sottotitolo = freezed,Object? estratto = freezed,Object? immagine = freezed,Object? sezione = freezed,Object? tempoLettura = null,Object? tags = null,Object? lang = freezed,Object? autore = freezed,Object? pubblicatoIl = freezed,Object? aggiornatoIl = freezed,Object? inEvidenza = null,Object? soggetto = freezed,}) {
  return _then(ArticoloBreve(
slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,titolo: null == titolo ? _self.titolo : titolo // ignore: cast_nullable_to_non_nullable
as String,sottotitolo: freezed == sottotitolo ? _self.sottotitolo : sottotitolo // ignore: cast_nullable_to_non_nullable
as String?,estratto: freezed == estratto ? _self.estratto : estratto // ignore: cast_nullable_to_non_nullable
as String?,immagine: freezed == immagine ? _self.immagine : immagine // ignore: cast_nullable_to_non_nullable
as ImmagineArticolo?,sezione: freezed == sezione ? _self.sezione : sezione // ignore: cast_nullable_to_non_nullable
as Voce?,tempoLettura: null == tempoLettura ? _self.tempoLettura : tempoLettura // ignore: cast_nullable_to_non_nullable
as int,tags: null == tags ? _self.tags : tags // ignore: cast_nullable_to_non_nullable
as List<Voce>,lang: freezed == lang ? _self.lang : lang // ignore: cast_nullable_to_non_nullable
as String?,autore: freezed == autore ? _self.autore : autore // ignore: cast_nullable_to_non_nullable
as AutoreBlog?,pubblicatoIl: freezed == pubblicatoIl ? _self.pubblicatoIl : pubblicatoIl // ignore: cast_nullable_to_non_nullable
as String?,aggiornatoIl: freezed == aggiornatoIl ? _self.aggiornatoIl : aggiornatoIl // ignore: cast_nullable_to_non_nullable
as String?,inEvidenza: null == inEvidenza ? _self.inEvidenza : inEvidenza // ignore: cast_nullable_to_non_nullable
as bool,soggetto: freezed == soggetto ? _self.soggetto : soggetto // ignore: cast_nullable_to_non_nullable
as SoggettoArticolo?,
  ));
}
/// Create a copy of ArticoloBreve
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ImmagineArticoloCopyWith<$Res>? get immagine {
    if (_self.immagine == null) {
    return null;
  }

  return $ImmagineArticoloCopyWith<$Res>(_self.immagine!, (value) {
    return _then(_self.copyWith(immagine: value));
  });
}/// Create a copy of ArticoloBreve
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$VoceCopyWith<$Res>? get sezione {
    if (_self.sezione == null) {
    return null;
  }

  return $VoceCopyWith<$Res>(_self.sezione!, (value) {
    return _then(_self.copyWith(sezione: value));
  });
}/// Create a copy of ArticoloBreve
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$AutoreBlogCopyWith<$Res>? get autore {
    if (_self.autore == null) {
    return null;
  }

  return $AutoreBlogCopyWith<$Res>(_self.autore!, (value) {
    return _then(_self.copyWith(autore: value));
  });
}/// Create a copy of ArticoloBreve
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$SoggettoArticoloCopyWith<$Res>? get soggetto {
    if (_self.soggetto == null) {
    return null;
  }

  return $SoggettoArticoloCopyWith<$Res>(_self.soggetto!, (value) {
    return _then(_self.copyWith(soggetto: value));
  });
}
}


/// Adds pattern-matching-related methods to [ArticoloBreve].
extension ArticoloBrevePatterns on ArticoloBreve {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ArticoloBreve value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ArticoloBreve() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ArticoloBreve value)  $default,){
final _that = this;
switch (_that) {
case _ArticoloBreve():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ArticoloBreve value)?  $default,){
final _that = this;
switch (_that) {
case _ArticoloBreve() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String slug,  String titolo,  String? sottotitolo,  String? estratto,  ImmagineArticolo? immagine,  Voce? sezione,  int tempoLettura,  List<Voce> tags,  String? lang,  AutoreBlog? autore,  String? pubblicatoIl,  String? aggiornatoIl,  bool inEvidenza,  SoggettoArticolo? soggetto)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ArticoloBreve() when $default != null:
return $default(_that.slug,_that.titolo,_that.sottotitolo,_that.estratto,_that.immagine,_that.sezione,_that.tempoLettura,_that.tags,_that.lang,_that.autore,_that.pubblicatoIl,_that.aggiornatoIl,_that.inEvidenza,_that.soggetto);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String slug,  String titolo,  String? sottotitolo,  String? estratto,  ImmagineArticolo? immagine,  Voce? sezione,  int tempoLettura,  List<Voce> tags,  String? lang,  AutoreBlog? autore,  String? pubblicatoIl,  String? aggiornatoIl,  bool inEvidenza,  SoggettoArticolo? soggetto)  $default,) {final _that = this;
switch (_that) {
case _ArticoloBreve():
return $default(_that.slug,_that.titolo,_that.sottotitolo,_that.estratto,_that.immagine,_that.sezione,_that.tempoLettura,_that.tags,_that.lang,_that.autore,_that.pubblicatoIl,_that.aggiornatoIl,_that.inEvidenza,_that.soggetto);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String slug,  String titolo,  String? sottotitolo,  String? estratto,  ImmagineArticolo? immagine,  Voce? sezione,  int tempoLettura,  List<Voce> tags,  String? lang,  AutoreBlog? autore,  String? pubblicatoIl,  String? aggiornatoIl,  bool inEvidenza,  SoggettoArticolo? soggetto)?  $default,) {final _that = this;
switch (_that) {
case _ArticoloBreve() when $default != null:
return $default(_that.slug,_that.titolo,_that.sottotitolo,_that.estratto,_that.immagine,_that.sezione,_that.tempoLettura,_that.tags,_that.lang,_that.autore,_that.pubblicatoIl,_that.aggiornatoIl,_that.inEvidenza,_that.soggetto);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ArticoloBreve implements ArticoloBreve {
  const _ArticoloBreve({required this.slug, required this.titolo, this.sottotitolo, this.estratto, this.immagine, this.sezione, this.tempoLettura = 1,  List<Voce> tags = const <Voce>[], this.lang, this.autore, this.pubblicatoIl, this.aggiornatoIl, this.inEvidenza = false, this.soggetto}): _tags = tags;
  factory _ArticoloBreve.fromJson(Map<String, dynamic> json) => _$ArticoloBreveFromJson(json);

@override final  String slug;
@override final  String titolo;
@override final  String? sottotitolo;
@override final  String? estratto;
@override final  ImmagineArticolo? immagine;
@override final  Voce? sezione;
@override@JsonKey() final  int tempoLettura;
 final  List<Voce> _tags;
@override@JsonKey() List<Voce> get tags {
  if (_tags is EqualUnmodifiableListView) return _tags;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_tags);
}

@override final  String? lang;
@override final  AutoreBlog? autore;
@override final  String? pubblicatoIl;
@override final  String? aggiornatoIl;
@override@JsonKey() final  bool inEvidenza;
/// La carta o la stesa di cui parla (v9.4), o null.
@override final  SoggettoArticolo? soggetto;

/// Create a copy of ArticoloBreve
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ArticoloBreveCopyWith<_ArticoloBreve> get copyWith => __$ArticoloBreveCopyWithImpl<_ArticoloBreve>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ArticoloBreveToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _ArticoloBreve&&(identical(other.slug, slug) || other.slug == slug)&&(identical(other.titolo, titolo) || other.titolo == titolo)&&(identical(other.sottotitolo, sottotitolo) || other.sottotitolo == sottotitolo)&&(identical(other.estratto, estratto) || other.estratto == estratto)&&(identical(other.immagine, immagine) || other.immagine == immagine)&&(identical(other.sezione, sezione) || other.sezione == sezione)&&(identical(other.tempoLettura, tempoLettura) || other.tempoLettura == tempoLettura)&&const DeepCollectionEquality().equals(other.tags, _tags)&&(identical(other.lang, lang) || other.lang == lang)&&(identical(other.autore, autore) || other.autore == autore)&&(identical(other.pubblicatoIl, pubblicatoIl) || other.pubblicatoIl == pubblicatoIl)&&(identical(other.aggiornatoIl, aggiornatoIl) || other.aggiornatoIl == aggiornatoIl)&&(identical(other.inEvidenza, inEvidenza) || other.inEvidenza == inEvidenza)&&(identical(other.soggetto, soggetto) || other.soggetto == soggetto));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,slug,titolo,sottotitolo,estratto,immagine,sezione,tempoLettura,const DeepCollectionEquality().hash(_tags),lang,autore,pubblicatoIl,aggiornatoIl,inEvidenza,soggetto);
}

@override
String toString() {
    return 'ArticoloBreve(slug: $slug, titolo: $titolo, sottotitolo: $sottotitolo, estratto: $estratto, immagine: $immagine, sezione: $sezione, tempoLettura: $tempoLettura, tags: $tags, lang: $lang, autore: $autore, pubblicatoIl: $pubblicatoIl, aggiornatoIl: $aggiornatoIl, inEvidenza: $inEvidenza, soggetto: $soggetto)';
}


}

/// @nodoc
abstract mixin class _$ArticoloBreveCopyWith<$Res> implements $ArticoloBreveCopyWith<$Res> {
  factory _$ArticoloBreveCopyWith(_ArticoloBreve value, $Res Function(_ArticoloBreve) _then) = __$ArticoloBreveCopyWithImpl;
@override @useResult
$Res call({
 String slug, String titolo, String? sottotitolo, String? estratto, ImmagineArticolo? immagine, Voce? sezione, int tempoLettura, List<Voce> tags, String? lang, AutoreBlog? autore, String? pubblicatoIl, String? aggiornatoIl, bool inEvidenza, SoggettoArticolo? soggetto
});


@override $ImmagineArticoloCopyWith<$Res>? get immagine;@override $VoceCopyWith<$Res>? get sezione;@override $AutoreBlogCopyWith<$Res>? get autore;@override $SoggettoArticoloCopyWith<$Res>? get soggetto;

}
/// @nodoc
class __$ArticoloBreveCopyWithImpl<$Res>
    implements _$ArticoloBreveCopyWith<$Res> {
  __$ArticoloBreveCopyWithImpl(this._self, this._then);

  final _ArticoloBreve _self;
  final $Res Function(_ArticoloBreve) _then;

/// Create a copy of ArticoloBreve
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? slug = null,Object? titolo = null,Object? sottotitolo = freezed,Object? estratto = freezed,Object? immagine = freezed,Object? sezione = freezed,Object? tempoLettura = null,Object? tags = null,Object? lang = freezed,Object? autore = freezed,Object? pubblicatoIl = freezed,Object? aggiornatoIl = freezed,Object? inEvidenza = null,Object? soggetto = freezed,}) {
  return _then(_ArticoloBreve(
slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,titolo: null == titolo ? _self.titolo : titolo // ignore: cast_nullable_to_non_nullable
as String,sottotitolo: freezed == sottotitolo ? _self.sottotitolo : sottotitolo // ignore: cast_nullable_to_non_nullable
as String?,estratto: freezed == estratto ? _self.estratto : estratto // ignore: cast_nullable_to_non_nullable
as String?,immagine: freezed == immagine ? _self.immagine : immagine // ignore: cast_nullable_to_non_nullable
as ImmagineArticolo?,sezione: freezed == sezione ? _self.sezione : sezione // ignore: cast_nullable_to_non_nullable
as Voce?,tempoLettura: null == tempoLettura ? _self.tempoLettura : tempoLettura // ignore: cast_nullable_to_non_nullable
as int,tags: null == tags ? _self._tags : tags // ignore: cast_nullable_to_non_nullable
as List<Voce>,lang: freezed == lang ? _self.lang : lang // ignore: cast_nullable_to_non_nullable
as String?,autore: freezed == autore ? _self.autore : autore // ignore: cast_nullable_to_non_nullable
as AutoreBlog?,pubblicatoIl: freezed == pubblicatoIl ? _self.pubblicatoIl : pubblicatoIl // ignore: cast_nullable_to_non_nullable
as String?,aggiornatoIl: freezed == aggiornatoIl ? _self.aggiornatoIl : aggiornatoIl // ignore: cast_nullable_to_non_nullable
as String?,inEvidenza: null == inEvidenza ? _self.inEvidenza : inEvidenza // ignore: cast_nullable_to_non_nullable
as bool,soggetto: freezed == soggetto ? _self.soggetto : soggetto // ignore: cast_nullable_to_non_nullable
as SoggettoArticolo?,
  ));
}

/// Create a copy of ArticoloBreve
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ImmagineArticoloCopyWith<$Res>? get immagine {
    if (_self.immagine == null) {
    return null;
  }

  return $ImmagineArticoloCopyWith<$Res>(_self.immagine!, (value) {
    return _then(_self.copyWith(immagine: value));
  });
}/// Create a copy of ArticoloBreve
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$VoceCopyWith<$Res>? get sezione {
    if (_self.sezione == null) {
    return null;
  }

  return $VoceCopyWith<$Res>(_self.sezione!, (value) {
    return _then(_self.copyWith(sezione: value));
  });
}/// Create a copy of ArticoloBreve
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$AutoreBlogCopyWith<$Res>? get autore {
    if (_self.autore == null) {
    return null;
  }

  return $AutoreBlogCopyWith<$Res>(_self.autore!, (value) {
    return _then(_self.copyWith(autore: value));
  });
}/// Create a copy of ArticoloBreve
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$SoggettoArticoloCopyWith<$Res>? get soggetto {
    if (_self.soggetto == null) {
    return null;
  }

  return $SoggettoArticoloCopyWith<$Res>(_self.soggetto!, (value) {
    return _then(_self.copyWith(soggetto: value));
  });
}
}


/// @nodoc
mixin _$Nove {

 List<ArticoloBreve> get recenti; List<ArticoloBreve> get scelti;
/// Create a copy of Nove
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$NoveCopyWith<Nove> get copyWith => _$NoveCopyWithImpl<Nove>(this as Nove, _$identity);

  /// Serializes this Nove to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Nove;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Nove&&const DeepCollectionEquality().equals(other.recenti, _this.recenti)&&const DeepCollectionEquality().equals(other.scelti, _this.scelti));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Nove;
  return Object.hash(runtimeType,const DeepCollectionEquality().hash(_this.recenti),const DeepCollectionEquality().hash(_this.scelti));
}

@override
String toString() {
  final _this = this as Nove;
  return 'Nove(recenti: ${_this.recenti}, scelti: ${_this.scelti})';
}


}

/// @nodoc
abstract mixin class $NoveCopyWith<$Res>  {
  factory $NoveCopyWith(Nove value, $Res Function(Nove) _then) = _$NoveCopyWithImpl;
@useResult
$Res call({
 List<ArticoloBreve> recenti, List<ArticoloBreve> scelti
});




}
/// @nodoc
class _$NoveCopyWithImpl<$Res>
    implements $NoveCopyWith<$Res> {
  _$NoveCopyWithImpl(this._self, this._then);

  final Nove _self;
  final $Res Function(Nove) _then;

/// Create a copy of Nove
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? recenti = null,Object? scelti = null,}) {
  return _then(Nove(
recenti: null == recenti ? _self.recenti : recenti // ignore: cast_nullable_to_non_nullable
as List<ArticoloBreve>,scelti: null == scelti ? _self.scelti : scelti // ignore: cast_nullable_to_non_nullable
as List<ArticoloBreve>,
  ));
}

}


/// Adds pattern-matching-related methods to [Nove].
extension NovePatterns on Nove {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Nove value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Nove() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Nove value)  $default,){
final _that = this;
switch (_that) {
case _Nove():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Nove value)?  $default,){
final _that = this;
switch (_that) {
case _Nove() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( List<ArticoloBreve> recenti,  List<ArticoloBreve> scelti)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Nove() when $default != null:
return $default(_that.recenti,_that.scelti);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( List<ArticoloBreve> recenti,  List<ArticoloBreve> scelti)  $default,) {final _that = this;
switch (_that) {
case _Nove():
return $default(_that.recenti,_that.scelti);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( List<ArticoloBreve> recenti,  List<ArticoloBreve> scelti)?  $default,) {final _that = this;
switch (_that) {
case _Nove() when $default != null:
return $default(_that.recenti,_that.scelti);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Nove implements Nove {
  const _Nove({ List<ArticoloBreve> recenti = const <ArticoloBreve>[],  List<ArticoloBreve> scelti = const <ArticoloBreve>[]}): _recenti = recenti,_scelti = scelti;
  factory _Nove.fromJson(Map<String, dynamic> json) => _$NoveFromJson(json);

 final  List<ArticoloBreve> _recenti;
@override@JsonKey() List<ArticoloBreve> get recenti {
  if (_recenti is EqualUnmodifiableListView) return _recenti;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_recenti);
}

 final  List<ArticoloBreve> _scelti;
@override@JsonKey() List<ArticoloBreve> get scelti {
  if (_scelti is EqualUnmodifiableListView) return _scelti;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_scelti);
}


/// Create a copy of Nove
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$NoveCopyWith<_Nove> get copyWith => __$NoveCopyWithImpl<_Nove>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$NoveToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Nove&&const DeepCollectionEquality().equals(other.recenti, _recenti)&&const DeepCollectionEquality().equals(other.scelti, _scelti));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,const DeepCollectionEquality().hash(_recenti),const DeepCollectionEquality().hash(_scelti));
}

@override
String toString() {
    return 'Nove(recenti: $recenti, scelti: $scelti)';
}


}

/// @nodoc
abstract mixin class _$NoveCopyWith<$Res> implements $NoveCopyWith<$Res> {
  factory _$NoveCopyWith(_Nove value, $Res Function(_Nove) _then) = __$NoveCopyWithImpl;
@override @useResult
$Res call({
 List<ArticoloBreve> recenti, List<ArticoloBreve> scelti
});




}
/// @nodoc
class __$NoveCopyWithImpl<$Res>
    implements _$NoveCopyWith<$Res> {
  __$NoveCopyWithImpl(this._self, this._then);

  final _Nove _self;
  final $Res Function(_Nove) _then;

/// Create a copy of Nove
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? recenti = null,Object? scelti = null,}) {
  return _then(_Nove(
recenti: null == recenti ? _self._recenti : recenti // ignore: cast_nullable_to_non_nullable
as List<ArticoloBreve>,scelti: null == scelti ? _self._scelti : scelti // ignore: cast_nullable_to_non_nullable
as List<ArticoloBreve>,
  ));
}


}

// dart format on

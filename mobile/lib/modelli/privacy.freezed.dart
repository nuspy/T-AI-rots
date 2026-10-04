// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'privacy.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$StatoEtaAccount {

 int get anni; String? get paese; String? get confermataIl; bool get daConfermare; bool get sottoEta;
/// Create a copy of StatoEtaAccount
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$StatoEtaAccountCopyWith<StatoEtaAccount> get copyWith => _$StatoEtaAccountCopyWithImpl<StatoEtaAccount>(this as StatoEtaAccount, _$identity);

  /// Serializes this StatoEtaAccount to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as StatoEtaAccount;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is StatoEtaAccount&&(identical(other.anni, _this.anni) || other.anni == _this.anni)&&(identical(other.paese, _this.paese) || other.paese == _this.paese)&&(identical(other.confermataIl, _this.confermataIl) || other.confermataIl == _this.confermataIl)&&(identical(other.daConfermare, _this.daConfermare) || other.daConfermare == _this.daConfermare)&&(identical(other.sottoEta, _this.sottoEta) || other.sottoEta == _this.sottoEta));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as StatoEtaAccount;
  return Object.hash(runtimeType,_this.anni,_this.paese,_this.confermataIl,_this.daConfermare,_this.sottoEta);
}

@override
String toString() {
  final _this = this as StatoEtaAccount;
  return 'StatoEtaAccount(anni: ${_this.anni}, paese: ${_this.paese}, confermataIl: ${_this.confermataIl}, daConfermare: ${_this.daConfermare}, sottoEta: ${_this.sottoEta})';
}


}

/// @nodoc
abstract mixin class $StatoEtaAccountCopyWith<$Res>  {
  factory $StatoEtaAccountCopyWith(StatoEtaAccount value, $Res Function(StatoEtaAccount) _then) = _$StatoEtaAccountCopyWithImpl;
@useResult
$Res call({
 int anni, String? paese, String? confermataIl, bool daConfermare, bool sottoEta
});




}
/// @nodoc
class _$StatoEtaAccountCopyWithImpl<$Res>
    implements $StatoEtaAccountCopyWith<$Res> {
  _$StatoEtaAccountCopyWithImpl(this._self, this._then);

  final StatoEtaAccount _self;
  final $Res Function(StatoEtaAccount) _then;

/// Create a copy of StatoEtaAccount
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? anni = null,Object? paese = freezed,Object? confermataIl = freezed,Object? daConfermare = null,Object? sottoEta = null,}) {
  return _then(StatoEtaAccount(
anni: null == anni ? _self.anni : anni // ignore: cast_nullable_to_non_nullable
as int,paese: freezed == paese ? _self.paese : paese // ignore: cast_nullable_to_non_nullable
as String?,confermataIl: freezed == confermataIl ? _self.confermataIl : confermataIl // ignore: cast_nullable_to_non_nullable
as String?,daConfermare: null == daConfermare ? _self.daConfermare : daConfermare // ignore: cast_nullable_to_non_nullable
as bool,sottoEta: null == sottoEta ? _self.sottoEta : sottoEta // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [StatoEtaAccount].
extension StatoEtaAccountPatterns on StatoEtaAccount {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _StatoEtaAccount value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _StatoEtaAccount() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _StatoEtaAccount value)  $default,){
final _that = this;
switch (_that) {
case _StatoEtaAccount():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _StatoEtaAccount value)?  $default,){
final _that = this;
switch (_that) {
case _StatoEtaAccount() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int anni,  String? paese,  String? confermataIl,  bool daConfermare,  bool sottoEta)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _StatoEtaAccount() when $default != null:
return $default(_that.anni,_that.paese,_that.confermataIl,_that.daConfermare,_that.sottoEta);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int anni,  String? paese,  String? confermataIl,  bool daConfermare,  bool sottoEta)  $default,) {final _that = this;
switch (_that) {
case _StatoEtaAccount():
return $default(_that.anni,_that.paese,_that.confermataIl,_that.daConfermare,_that.sottoEta);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int anni,  String? paese,  String? confermataIl,  bool daConfermare,  bool sottoEta)?  $default,) {final _that = this;
switch (_that) {
case _StatoEtaAccount() when $default != null:
return $default(_that.anni,_that.paese,_that.confermataIl,_that.daConfermare,_that.sottoEta);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _StatoEtaAccount implements StatoEtaAccount {
  const _StatoEtaAccount({this.anni = 16, this.paese, this.confermataIl, this.daConfermare = false, this.sottoEta = false});
  factory _StatoEtaAccount.fromJson(Map<String, dynamic> json) => _$StatoEtaAccountFromJson(json);

@override@JsonKey() final  int anni;
@override final  String? paese;
@override final  String? confermataIl;
@override@JsonKey() final  bool daConfermare;
@override@JsonKey() final  bool sottoEta;

/// Create a copy of StatoEtaAccount
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$StatoEtaAccountCopyWith<_StatoEtaAccount> get copyWith => __$StatoEtaAccountCopyWithImpl<_StatoEtaAccount>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$StatoEtaAccountToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _StatoEtaAccount&&(identical(other.anni, anni) || other.anni == anni)&&(identical(other.paese, paese) || other.paese == paese)&&(identical(other.confermataIl, confermataIl) || other.confermataIl == confermataIl)&&(identical(other.daConfermare, daConfermare) || other.daConfermare == daConfermare)&&(identical(other.sottoEta, sottoEta) || other.sottoEta == sottoEta));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,anni,paese,confermataIl,daConfermare,sottoEta);
}

@override
String toString() {
    return 'StatoEtaAccount(anni: $anni, paese: $paese, confermataIl: $confermataIl, daConfermare: $daConfermare, sottoEta: $sottoEta)';
}


}

/// @nodoc
abstract mixin class _$StatoEtaAccountCopyWith<$Res> implements $StatoEtaAccountCopyWith<$Res> {
  factory _$StatoEtaAccountCopyWith(_StatoEtaAccount value, $Res Function(_StatoEtaAccount) _then) = __$StatoEtaAccountCopyWithImpl;
@override @useResult
$Res call({
 int anni, String? paese, String? confermataIl, bool daConfermare, bool sottoEta
});




}
/// @nodoc
class __$StatoEtaAccountCopyWithImpl<$Res>
    implements _$StatoEtaAccountCopyWith<$Res> {
  __$StatoEtaAccountCopyWithImpl(this._self, this._then);

  final _StatoEtaAccount _self;
  final $Res Function(_StatoEtaAccount) _then;

/// Create a copy of StatoEtaAccount
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? anni = null,Object? paese = freezed,Object? confermataIl = freezed,Object? daConfermare = null,Object? sottoEta = null,}) {
  return _then(_StatoEtaAccount(
anni: null == anni ? _self.anni : anni // ignore: cast_nullable_to_non_nullable
as int,paese: freezed == paese ? _self.paese : paese // ignore: cast_nullable_to_non_nullable
as String?,confermataIl: freezed == confermataIl ? _self.confermataIl : confermataIl // ignore: cast_nullable_to_non_nullable
as String?,daConfermare: null == daConfermare ? _self.daConfermare : daConfermare // ignore: cast_nullable_to_non_nullable
as bool,sottoEta: null == sottoEta ? _self.sottoEta : sottoEta // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}


/// @nodoc
mixin _$StatoCancellazione {

 String? get richiestaIl; String? get definitivaIl; String? get eseguitaIl; bool get annullabile; int get giorniRipensamento; bool? get sessioniChiuse;
/// Create a copy of StatoCancellazione
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$StatoCancellazioneCopyWith<StatoCancellazione> get copyWith => _$StatoCancellazioneCopyWithImpl<StatoCancellazione>(this as StatoCancellazione, _$identity);

  /// Serializes this StatoCancellazione to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as StatoCancellazione;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is StatoCancellazione&&(identical(other.richiestaIl, _this.richiestaIl) || other.richiestaIl == _this.richiestaIl)&&(identical(other.definitivaIl, _this.definitivaIl) || other.definitivaIl == _this.definitivaIl)&&(identical(other.eseguitaIl, _this.eseguitaIl) || other.eseguitaIl == _this.eseguitaIl)&&(identical(other.annullabile, _this.annullabile) || other.annullabile == _this.annullabile)&&(identical(other.giorniRipensamento, _this.giorniRipensamento) || other.giorniRipensamento == _this.giorniRipensamento)&&(identical(other.sessioniChiuse, _this.sessioniChiuse) || other.sessioniChiuse == _this.sessioniChiuse));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as StatoCancellazione;
  return Object.hash(runtimeType,_this.richiestaIl,_this.definitivaIl,_this.eseguitaIl,_this.annullabile,_this.giorniRipensamento,_this.sessioniChiuse);
}

@override
String toString() {
  final _this = this as StatoCancellazione;
  return 'StatoCancellazione(richiestaIl: ${_this.richiestaIl}, definitivaIl: ${_this.definitivaIl}, eseguitaIl: ${_this.eseguitaIl}, annullabile: ${_this.annullabile}, giorniRipensamento: ${_this.giorniRipensamento}, sessioniChiuse: ${_this.sessioniChiuse})';
}


}

/// @nodoc
abstract mixin class $StatoCancellazioneCopyWith<$Res>  {
  factory $StatoCancellazioneCopyWith(StatoCancellazione value, $Res Function(StatoCancellazione) _then) = _$StatoCancellazioneCopyWithImpl;
@useResult
$Res call({
 String? richiestaIl, String? definitivaIl, String? eseguitaIl, bool annullabile, int giorniRipensamento, bool? sessioniChiuse
});




}
/// @nodoc
class _$StatoCancellazioneCopyWithImpl<$Res>
    implements $StatoCancellazioneCopyWith<$Res> {
  _$StatoCancellazioneCopyWithImpl(this._self, this._then);

  final StatoCancellazione _self;
  final $Res Function(StatoCancellazione) _then;

/// Create a copy of StatoCancellazione
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? richiestaIl = freezed,Object? definitivaIl = freezed,Object? eseguitaIl = freezed,Object? annullabile = null,Object? giorniRipensamento = null,Object? sessioniChiuse = freezed,}) {
  return _then(StatoCancellazione(
richiestaIl: freezed == richiestaIl ? _self.richiestaIl : richiestaIl // ignore: cast_nullable_to_non_nullable
as String?,definitivaIl: freezed == definitivaIl ? _self.definitivaIl : definitivaIl // ignore: cast_nullable_to_non_nullable
as String?,eseguitaIl: freezed == eseguitaIl ? _self.eseguitaIl : eseguitaIl // ignore: cast_nullable_to_non_nullable
as String?,annullabile: null == annullabile ? _self.annullabile : annullabile // ignore: cast_nullable_to_non_nullable
as bool,giorniRipensamento: null == giorniRipensamento ? _self.giorniRipensamento : giorniRipensamento // ignore: cast_nullable_to_non_nullable
as int,sessioniChiuse: freezed == sessioniChiuse ? _self.sessioniChiuse : sessioniChiuse // ignore: cast_nullable_to_non_nullable
as bool?,
  ));
}

}


/// Adds pattern-matching-related methods to [StatoCancellazione].
extension StatoCancellazionePatterns on StatoCancellazione {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _StatoCancellazione value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _StatoCancellazione() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _StatoCancellazione value)  $default,){
final _that = this;
switch (_that) {
case _StatoCancellazione():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _StatoCancellazione value)?  $default,){
final _that = this;
switch (_that) {
case _StatoCancellazione() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? richiestaIl,  String? definitivaIl,  String? eseguitaIl,  bool annullabile,  int giorniRipensamento,  bool? sessioniChiuse)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _StatoCancellazione() when $default != null:
return $default(_that.richiestaIl,_that.definitivaIl,_that.eseguitaIl,_that.annullabile,_that.giorniRipensamento,_that.sessioniChiuse);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? richiestaIl,  String? definitivaIl,  String? eseguitaIl,  bool annullabile,  int giorniRipensamento,  bool? sessioniChiuse)  $default,) {final _that = this;
switch (_that) {
case _StatoCancellazione():
return $default(_that.richiestaIl,_that.definitivaIl,_that.eseguitaIl,_that.annullabile,_that.giorniRipensamento,_that.sessioniChiuse);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? richiestaIl,  String? definitivaIl,  String? eseguitaIl,  bool annullabile,  int giorniRipensamento,  bool? sessioniChiuse)?  $default,) {final _that = this;
switch (_that) {
case _StatoCancellazione() when $default != null:
return $default(_that.richiestaIl,_that.definitivaIl,_that.eseguitaIl,_that.annullabile,_that.giorniRipensamento,_that.sessioniChiuse);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _StatoCancellazione implements StatoCancellazione {
  const _StatoCancellazione({this.richiestaIl, this.definitivaIl, this.eseguitaIl, this.annullabile = false, this.giorniRipensamento = 30, this.sessioniChiuse});
  factory _StatoCancellazione.fromJson(Map<String, dynamic> json) => _$StatoCancellazioneFromJson(json);

@override final  String? richiestaIl;
@override final  String? definitivaIl;
@override final  String? eseguitaIl;
@override@JsonKey() final  bool annullabile;
@override@JsonKey() final  int giorniRipensamento;
@override final  bool? sessioniChiuse;

/// Create a copy of StatoCancellazione
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$StatoCancellazioneCopyWith<_StatoCancellazione> get copyWith => __$StatoCancellazioneCopyWithImpl<_StatoCancellazione>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$StatoCancellazioneToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _StatoCancellazione&&(identical(other.richiestaIl, richiestaIl) || other.richiestaIl == richiestaIl)&&(identical(other.definitivaIl, definitivaIl) || other.definitivaIl == definitivaIl)&&(identical(other.eseguitaIl, eseguitaIl) || other.eseguitaIl == eseguitaIl)&&(identical(other.annullabile, annullabile) || other.annullabile == annullabile)&&(identical(other.giorniRipensamento, giorniRipensamento) || other.giorniRipensamento == giorniRipensamento)&&(identical(other.sessioniChiuse, sessioniChiuse) || other.sessioniChiuse == sessioniChiuse));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,richiestaIl,definitivaIl,eseguitaIl,annullabile,giorniRipensamento,sessioniChiuse);
}

@override
String toString() {
    return 'StatoCancellazione(richiestaIl: $richiestaIl, definitivaIl: $definitivaIl, eseguitaIl: $eseguitaIl, annullabile: $annullabile, giorniRipensamento: $giorniRipensamento, sessioniChiuse: $sessioniChiuse)';
}


}

/// @nodoc
abstract mixin class _$StatoCancellazioneCopyWith<$Res> implements $StatoCancellazioneCopyWith<$Res> {
  factory _$StatoCancellazioneCopyWith(_StatoCancellazione value, $Res Function(_StatoCancellazione) _then) = __$StatoCancellazioneCopyWithImpl;
@override @useResult
$Res call({
 String? richiestaIl, String? definitivaIl, String? eseguitaIl, bool annullabile, int giorniRipensamento, bool? sessioniChiuse
});




}
/// @nodoc
class __$StatoCancellazioneCopyWithImpl<$Res>
    implements _$StatoCancellazioneCopyWith<$Res> {
  __$StatoCancellazioneCopyWithImpl(this._self, this._then);

  final _StatoCancellazione _self;
  final $Res Function(_StatoCancellazione) _then;

/// Create a copy of StatoCancellazione
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? richiestaIl = freezed,Object? definitivaIl = freezed,Object? eseguitaIl = freezed,Object? annullabile = null,Object? giorniRipensamento = null,Object? sessioniChiuse = freezed,}) {
  return _then(_StatoCancellazione(
richiestaIl: freezed == richiestaIl ? _self.richiestaIl : richiestaIl // ignore: cast_nullable_to_non_nullable
as String?,definitivaIl: freezed == definitivaIl ? _self.definitivaIl : definitivaIl // ignore: cast_nullable_to_non_nullable
as String?,eseguitaIl: freezed == eseguitaIl ? _self.eseguitaIl : eseguitaIl // ignore: cast_nullable_to_non_nullable
as String?,annullabile: null == annullabile ? _self.annullabile : annullabile // ignore: cast_nullable_to_non_nullable
as bool,giorniRipensamento: null == giorniRipensamento ? _self.giorniRipensamento : giorniRipensamento // ignore: cast_nullable_to_non_nullable
as int,sessioniChiuse: freezed == sessioniChiuse ? _self.sessioniChiuse : sessioniChiuse // ignore: cast_nullable_to_non_nullable
as bool?,
  ));
}


}


/// @nodoc
mixin _$StatoEsportazione {

 String? get ultimaIl; String? get prossimaDal;
/// Create a copy of StatoEsportazione
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$StatoEsportazioneCopyWith<StatoEsportazione> get copyWith => _$StatoEsportazioneCopyWithImpl<StatoEsportazione>(this as StatoEsportazione, _$identity);

  /// Serializes this StatoEsportazione to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as StatoEsportazione;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is StatoEsportazione&&(identical(other.ultimaIl, _this.ultimaIl) || other.ultimaIl == _this.ultimaIl)&&(identical(other.prossimaDal, _this.prossimaDal) || other.prossimaDal == _this.prossimaDal));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as StatoEsportazione;
  return Object.hash(runtimeType,_this.ultimaIl,_this.prossimaDal);
}

@override
String toString() {
  final _this = this as StatoEsportazione;
  return 'StatoEsportazione(ultimaIl: ${_this.ultimaIl}, prossimaDal: ${_this.prossimaDal})';
}


}

/// @nodoc
abstract mixin class $StatoEsportazioneCopyWith<$Res>  {
  factory $StatoEsportazioneCopyWith(StatoEsportazione value, $Res Function(StatoEsportazione) _then) = _$StatoEsportazioneCopyWithImpl;
@useResult
$Res call({
 String? ultimaIl, String? prossimaDal
});




}
/// @nodoc
class _$StatoEsportazioneCopyWithImpl<$Res>
    implements $StatoEsportazioneCopyWith<$Res> {
  _$StatoEsportazioneCopyWithImpl(this._self, this._then);

  final StatoEsportazione _self;
  final $Res Function(StatoEsportazione) _then;

/// Create a copy of StatoEsportazione
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? ultimaIl = freezed,Object? prossimaDal = freezed,}) {
  return _then(StatoEsportazione(
ultimaIl: freezed == ultimaIl ? _self.ultimaIl : ultimaIl // ignore: cast_nullable_to_non_nullable
as String?,prossimaDal: freezed == prossimaDal ? _self.prossimaDal : prossimaDal // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [StatoEsportazione].
extension StatoEsportazionePatterns on StatoEsportazione {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _StatoEsportazione value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _StatoEsportazione() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _StatoEsportazione value)  $default,){
final _that = this;
switch (_that) {
case _StatoEsportazione():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _StatoEsportazione value)?  $default,){
final _that = this;
switch (_that) {
case _StatoEsportazione() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? ultimaIl,  String? prossimaDal)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _StatoEsportazione() when $default != null:
return $default(_that.ultimaIl,_that.prossimaDal);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? ultimaIl,  String? prossimaDal)  $default,) {final _that = this;
switch (_that) {
case _StatoEsportazione():
return $default(_that.ultimaIl,_that.prossimaDal);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? ultimaIl,  String? prossimaDal)?  $default,) {final _that = this;
switch (_that) {
case _StatoEsportazione() when $default != null:
return $default(_that.ultimaIl,_that.prossimaDal);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _StatoEsportazione implements StatoEsportazione {
  const _StatoEsportazione({this.ultimaIl, this.prossimaDal});
  factory _StatoEsportazione.fromJson(Map<String, dynamic> json) => _$StatoEsportazioneFromJson(json);

@override final  String? ultimaIl;
@override final  String? prossimaDal;

/// Create a copy of StatoEsportazione
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$StatoEsportazioneCopyWith<_StatoEsportazione> get copyWith => __$StatoEsportazioneCopyWithImpl<_StatoEsportazione>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$StatoEsportazioneToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _StatoEsportazione&&(identical(other.ultimaIl, ultimaIl) || other.ultimaIl == ultimaIl)&&(identical(other.prossimaDal, prossimaDal) || other.prossimaDal == prossimaDal));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,ultimaIl,prossimaDal);
}

@override
String toString() {
    return 'StatoEsportazione(ultimaIl: $ultimaIl, prossimaDal: $prossimaDal)';
}


}

/// @nodoc
abstract mixin class _$StatoEsportazioneCopyWith<$Res> implements $StatoEsportazioneCopyWith<$Res> {
  factory _$StatoEsportazioneCopyWith(_StatoEsportazione value, $Res Function(_StatoEsportazione) _then) = __$StatoEsportazioneCopyWithImpl;
@override @useResult
$Res call({
 String? ultimaIl, String? prossimaDal
});




}
/// @nodoc
class __$StatoEsportazioneCopyWithImpl<$Res>
    implements _$StatoEsportazioneCopyWith<$Res> {
  __$StatoEsportazioneCopyWithImpl(this._self, this._then);

  final _StatoEsportazione _self;
  final $Res Function(_StatoEsportazione) _then;

/// Create a copy of StatoEsportazione
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? ultimaIl = freezed,Object? prossimaDal = freezed,}) {
  return _then(_StatoEsportazione(
ultimaIl: freezed == ultimaIl ? _self.ultimaIl : ultimaIl // ignore: cast_nullable_to_non_nullable
as String?,prossimaDal: freezed == prossimaDal ? _self.prossimaDal : prossimaDal // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$SceltaRegistrata {

 String get valore; String get versione; String? get il;
/// Create a copy of SceltaRegistrata
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SceltaRegistrataCopyWith<SceltaRegistrata> get copyWith => _$SceltaRegistrataCopyWithImpl<SceltaRegistrata>(this as SceltaRegistrata, _$identity);

  /// Serializes this SceltaRegistrata to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as SceltaRegistrata;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SceltaRegistrata&&(identical(other.valore, _this.valore) || other.valore == _this.valore)&&(identical(other.versione, _this.versione) || other.versione == _this.versione)&&(identical(other.il, _this.il) || other.il == _this.il));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as SceltaRegistrata;
  return Object.hash(runtimeType,_this.valore,_this.versione,_this.il);
}

@override
String toString() {
  final _this = this as SceltaRegistrata;
  return 'SceltaRegistrata(valore: ${_this.valore}, versione: ${_this.versione}, il: ${_this.il})';
}


}

/// @nodoc
abstract mixin class $SceltaRegistrataCopyWith<$Res>  {
  factory $SceltaRegistrataCopyWith(SceltaRegistrata value, $Res Function(SceltaRegistrata) _then) = _$SceltaRegistrataCopyWithImpl;
@useResult
$Res call({
 String valore, String versione, String? il
});




}
/// @nodoc
class _$SceltaRegistrataCopyWithImpl<$Res>
    implements $SceltaRegistrataCopyWith<$Res> {
  _$SceltaRegistrataCopyWithImpl(this._self, this._then);

  final SceltaRegistrata _self;
  final $Res Function(SceltaRegistrata) _then;

/// Create a copy of SceltaRegistrata
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? valore = null,Object? versione = null,Object? il = freezed,}) {
  return _then(SceltaRegistrata(
valore: null == valore ? _self.valore : valore // ignore: cast_nullable_to_non_nullable
as String,versione: null == versione ? _self.versione : versione // ignore: cast_nullable_to_non_nullable
as String,il: freezed == il ? _self.il : il // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [SceltaRegistrata].
extension SceltaRegistrataPatterns on SceltaRegistrata {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _SceltaRegistrata value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _SceltaRegistrata() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _SceltaRegistrata value)  $default,){
final _that = this;
switch (_that) {
case _SceltaRegistrata():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _SceltaRegistrata value)?  $default,){
final _that = this;
switch (_that) {
case _SceltaRegistrata() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String valore,  String versione,  String? il)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _SceltaRegistrata() when $default != null:
return $default(_that.valore,_that.versione,_that.il);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String valore,  String versione,  String? il)  $default,) {final _that = this;
switch (_that) {
case _SceltaRegistrata():
return $default(_that.valore,_that.versione,_that.il);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String valore,  String versione,  String? il)?  $default,) {final _that = this;
switch (_that) {
case _SceltaRegistrata() when $default != null:
return $default(_that.valore,_that.versione,_that.il);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _SceltaRegistrata implements SceltaRegistrata {
  const _SceltaRegistrata({required this.valore, this.versione = '', this.il});
  factory _SceltaRegistrata.fromJson(Map<String, dynamic> json) => _$SceltaRegistrataFromJson(json);

@override final  String valore;
@override@JsonKey() final  String versione;
@override final  String? il;

/// Create a copy of SceltaRegistrata
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SceltaRegistrataCopyWith<_SceltaRegistrata> get copyWith => __$SceltaRegistrataCopyWithImpl<_SceltaRegistrata>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SceltaRegistrataToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _SceltaRegistrata&&(identical(other.valore, valore) || other.valore == valore)&&(identical(other.versione, versione) || other.versione == versione)&&(identical(other.il, il) || other.il == il));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,valore,versione,il);
}

@override
String toString() {
    return 'SceltaRegistrata(valore: $valore, versione: $versione, il: $il)';
}


}

/// @nodoc
abstract mixin class _$SceltaRegistrataCopyWith<$Res> implements $SceltaRegistrataCopyWith<$Res> {
  factory _$SceltaRegistrataCopyWith(_SceltaRegistrata value, $Res Function(_SceltaRegistrata) _then) = __$SceltaRegistrataCopyWithImpl;
@override @useResult
$Res call({
 String valore, String versione, String? il
});




}
/// @nodoc
class __$SceltaRegistrataCopyWithImpl<$Res>
    implements _$SceltaRegistrataCopyWith<$Res> {
  __$SceltaRegistrataCopyWithImpl(this._self, this._then);

  final _SceltaRegistrata _self;
  final $Res Function(_SceltaRegistrata) _then;

/// Create a copy of SceltaRegistrata
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? valore = null,Object? versione = null,Object? il = freezed,}) {
  return _then(_SceltaRegistrata(
valore: null == valore ? _self.valore : valore // ignore: cast_nullable_to_non_nullable
as String,versione: null == versione ? _self.versione : versione // ignore: cast_nullable_to_non_nullable
as String,il: freezed == il ? _self.il : il // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$StatoPrivacy {

 StatoEtaAccount get eta; StatoEsportazione get esportazione; Map<String, SceltaRegistrata> get consensi; StatoCancellazione get cancellazione;
/// Create a copy of StatoPrivacy
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$StatoPrivacyCopyWith<StatoPrivacy> get copyWith => _$StatoPrivacyCopyWithImpl<StatoPrivacy>(this as StatoPrivacy, _$identity);

  /// Serializes this StatoPrivacy to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as StatoPrivacy;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is StatoPrivacy&&(identical(other.eta, _this.eta) || other.eta == _this.eta)&&(identical(other.esportazione, _this.esportazione) || other.esportazione == _this.esportazione)&&const DeepCollectionEquality().equals(other.consensi, _this.consensi)&&(identical(other.cancellazione, _this.cancellazione) || other.cancellazione == _this.cancellazione));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as StatoPrivacy;
  return Object.hash(runtimeType,_this.eta,_this.esportazione,const DeepCollectionEquality().hash(_this.consensi),_this.cancellazione);
}

@override
String toString() {
  final _this = this as StatoPrivacy;
  return 'StatoPrivacy(eta: ${_this.eta}, esportazione: ${_this.esportazione}, consensi: ${_this.consensi}, cancellazione: ${_this.cancellazione})';
}


}

/// @nodoc
abstract mixin class $StatoPrivacyCopyWith<$Res>  {
  factory $StatoPrivacyCopyWith(StatoPrivacy value, $Res Function(StatoPrivacy) _then) = _$StatoPrivacyCopyWithImpl;
@useResult
$Res call({
 StatoEtaAccount eta, StatoEsportazione esportazione, Map<String, SceltaRegistrata> consensi, StatoCancellazione cancellazione
});


$StatoEtaAccountCopyWith<$Res> get eta;$StatoEsportazioneCopyWith<$Res> get esportazione;$StatoCancellazioneCopyWith<$Res> get cancellazione;

}
/// @nodoc
class _$StatoPrivacyCopyWithImpl<$Res>
    implements $StatoPrivacyCopyWith<$Res> {
  _$StatoPrivacyCopyWithImpl(this._self, this._then);

  final StatoPrivacy _self;
  final $Res Function(StatoPrivacy) _then;

/// Create a copy of StatoPrivacy
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? eta = null,Object? esportazione = null,Object? consensi = null,Object? cancellazione = null,}) {
  return _then(StatoPrivacy(
eta: null == eta ? _self.eta : eta // ignore: cast_nullable_to_non_nullable
as StatoEtaAccount,esportazione: null == esportazione ? _self.esportazione : esportazione // ignore: cast_nullable_to_non_nullable
as StatoEsportazione,consensi: null == consensi ? _self.consensi : consensi // ignore: cast_nullable_to_non_nullable
as Map<String, SceltaRegistrata>,cancellazione: null == cancellazione ? _self.cancellazione : cancellazione // ignore: cast_nullable_to_non_nullable
as StatoCancellazione,
  ));
}
/// Create a copy of StatoPrivacy
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$StatoEtaAccountCopyWith<$Res> get eta {
  
  return $StatoEtaAccountCopyWith<$Res>(_self.eta, (value) {
    return _then(_self.copyWith(eta: value));
  });
}/// Create a copy of StatoPrivacy
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$StatoEsportazioneCopyWith<$Res> get esportazione {
  
  return $StatoEsportazioneCopyWith<$Res>(_self.esportazione, (value) {
    return _then(_self.copyWith(esportazione: value));
  });
}/// Create a copy of StatoPrivacy
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$StatoCancellazioneCopyWith<$Res> get cancellazione {
  
  return $StatoCancellazioneCopyWith<$Res>(_self.cancellazione, (value) {
    return _then(_self.copyWith(cancellazione: value));
  });
}
}


/// Adds pattern-matching-related methods to [StatoPrivacy].
extension StatoPrivacyPatterns on StatoPrivacy {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _StatoPrivacy value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _StatoPrivacy() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _StatoPrivacy value)  $default,){
final _that = this;
switch (_that) {
case _StatoPrivacy():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _StatoPrivacy value)?  $default,){
final _that = this;
switch (_that) {
case _StatoPrivacy() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( StatoEtaAccount eta,  StatoEsportazione esportazione,  Map<String, SceltaRegistrata> consensi,  StatoCancellazione cancellazione)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _StatoPrivacy() when $default != null:
return $default(_that.eta,_that.esportazione,_that.consensi,_that.cancellazione);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( StatoEtaAccount eta,  StatoEsportazione esportazione,  Map<String, SceltaRegistrata> consensi,  StatoCancellazione cancellazione)  $default,) {final _that = this;
switch (_that) {
case _StatoPrivacy():
return $default(_that.eta,_that.esportazione,_that.consensi,_that.cancellazione);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( StatoEtaAccount eta,  StatoEsportazione esportazione,  Map<String, SceltaRegistrata> consensi,  StatoCancellazione cancellazione)?  $default,) {final _that = this;
switch (_that) {
case _StatoPrivacy() when $default != null:
return $default(_that.eta,_that.esportazione,_that.consensi,_that.cancellazione);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _StatoPrivacy implements StatoPrivacy {
  const _StatoPrivacy({this.eta = const StatoEtaAccount(), this.esportazione = const StatoEsportazione(),  Map<String, SceltaRegistrata> consensi = const <String, SceltaRegistrata>{}, this.cancellazione = const StatoCancellazione()}): _consensi = consensi;
  factory _StatoPrivacy.fromJson(Map<String, dynamic> json) => _$StatoPrivacyFromJson(json);

@override@JsonKey() final  StatoEtaAccount eta;
@override@JsonKey() final  StatoEsportazione esportazione;
 final  Map<String, SceltaRegistrata> _consensi;
@override@JsonKey() Map<String, SceltaRegistrata> get consensi {
  if (_consensi is EqualUnmodifiableMapView) return _consensi;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_consensi);
}

@override@JsonKey() final  StatoCancellazione cancellazione;

/// Create a copy of StatoPrivacy
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$StatoPrivacyCopyWith<_StatoPrivacy> get copyWith => __$StatoPrivacyCopyWithImpl<_StatoPrivacy>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$StatoPrivacyToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _StatoPrivacy&&(identical(other.eta, eta) || other.eta == eta)&&(identical(other.esportazione, esportazione) || other.esportazione == esportazione)&&const DeepCollectionEquality().equals(other.consensi, _consensi)&&(identical(other.cancellazione, cancellazione) || other.cancellazione == cancellazione));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,eta,esportazione,const DeepCollectionEquality().hash(_consensi),cancellazione);
}

@override
String toString() {
    return 'StatoPrivacy(eta: $eta, esportazione: $esportazione, consensi: $consensi, cancellazione: $cancellazione)';
}


}

/// @nodoc
abstract mixin class _$StatoPrivacyCopyWith<$Res> implements $StatoPrivacyCopyWith<$Res> {
  factory _$StatoPrivacyCopyWith(_StatoPrivacy value, $Res Function(_StatoPrivacy) _then) = __$StatoPrivacyCopyWithImpl;
@override @useResult
$Res call({
 StatoEtaAccount eta, StatoEsportazione esportazione, Map<String, SceltaRegistrata> consensi, StatoCancellazione cancellazione
});


@override $StatoEtaAccountCopyWith<$Res> get eta;@override $StatoEsportazioneCopyWith<$Res> get esportazione;@override $StatoCancellazioneCopyWith<$Res> get cancellazione;

}
/// @nodoc
class __$StatoPrivacyCopyWithImpl<$Res>
    implements _$StatoPrivacyCopyWith<$Res> {
  __$StatoPrivacyCopyWithImpl(this._self, this._then);

  final _StatoPrivacy _self;
  final $Res Function(_StatoPrivacy) _then;

/// Create a copy of StatoPrivacy
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? eta = null,Object? esportazione = null,Object? consensi = null,Object? cancellazione = null,}) {
  return _then(_StatoPrivacy(
eta: null == eta ? _self.eta : eta // ignore: cast_nullable_to_non_nullable
as StatoEtaAccount,esportazione: null == esportazione ? _self.esportazione : esportazione // ignore: cast_nullable_to_non_nullable
as StatoEsportazione,consensi: null == consensi ? _self._consensi : consensi // ignore: cast_nullable_to_non_nullable
as Map<String, SceltaRegistrata>,cancellazione: null == cancellazione ? _self.cancellazione : cancellazione // ignore: cast_nullable_to_non_nullable
as StatoCancellazione,
  ));
}

/// Create a copy of StatoPrivacy
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$StatoEtaAccountCopyWith<$Res> get eta {
  
  return $StatoEtaAccountCopyWith<$Res>(_self.eta, (value) {
    return _then(_self.copyWith(eta: value));
  });
}/// Create a copy of StatoPrivacy
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$StatoEsportazioneCopyWith<$Res> get esportazione {
  
  return $StatoEsportazioneCopyWith<$Res>(_self.esportazione, (value) {
    return _then(_self.copyWith(esportazione: value));
  });
}/// Create a copy of StatoPrivacy
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$StatoCancellazioneCopyWith<$Res> get cancellazione {
  
  return $StatoCancellazioneCopyWith<$Res>(_self.cancellazione, (value) {
    return _then(_self.copyWith(cancellazione: value));
  });
}
}


/// @nodoc
mixin _$Dpo {

 bool get nominato; String? get contatto;
/// Create a copy of Dpo
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DpoCopyWith<Dpo> get copyWith => _$DpoCopyWithImpl<Dpo>(this as Dpo, _$identity);

  /// Serializes this Dpo to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Dpo;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Dpo&&(identical(other.nominato, _this.nominato) || other.nominato == _this.nominato)&&(identical(other.contatto, _this.contatto) || other.contatto == _this.contatto));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Dpo;
  return Object.hash(runtimeType,_this.nominato,_this.contatto);
}

@override
String toString() {
  final _this = this as Dpo;
  return 'Dpo(nominato: ${_this.nominato}, contatto: ${_this.contatto})';
}


}

/// @nodoc
abstract mixin class $DpoCopyWith<$Res>  {
  factory $DpoCopyWith(Dpo value, $Res Function(Dpo) _then) = _$DpoCopyWithImpl;
@useResult
$Res call({
 bool nominato, String? contatto
});




}
/// @nodoc
class _$DpoCopyWithImpl<$Res>
    implements $DpoCopyWith<$Res> {
  _$DpoCopyWithImpl(this._self, this._then);

  final Dpo _self;
  final $Res Function(Dpo) _then;

/// Create a copy of Dpo
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? nominato = null,Object? contatto = freezed,}) {
  return _then(Dpo(
nominato: null == nominato ? _self.nominato : nominato // ignore: cast_nullable_to_non_nullable
as bool,contatto: freezed == contatto ? _self.contatto : contatto // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [Dpo].
extension DpoPatterns on Dpo {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Dpo value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Dpo() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Dpo value)  $default,){
final _that = this;
switch (_that) {
case _Dpo():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Dpo value)?  $default,){
final _that = this;
switch (_that) {
case _Dpo() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( bool nominato,  String? contatto)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Dpo() when $default != null:
return $default(_that.nominato,_that.contatto);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( bool nominato,  String? contatto)  $default,) {final _that = this;
switch (_that) {
case _Dpo():
return $default(_that.nominato,_that.contatto);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( bool nominato,  String? contatto)?  $default,) {final _that = this;
switch (_that) {
case _Dpo() when $default != null:
return $default(_that.nominato,_that.contatto);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Dpo implements Dpo {
  const _Dpo({this.nominato = false, this.contatto});
  factory _Dpo.fromJson(Map<String, dynamic> json) => _$DpoFromJson(json);

@override@JsonKey() final  bool nominato;
@override final  String? contatto;

/// Create a copy of Dpo
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DpoCopyWith<_Dpo> get copyWith => __$DpoCopyWithImpl<_Dpo>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$DpoToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Dpo&&(identical(other.nominato, nominato) || other.nominato == nominato)&&(identical(other.contatto, contatto) || other.contatto == contatto));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,nominato,contatto);
}

@override
String toString() {
    return 'Dpo(nominato: $nominato, contatto: $contatto)';
}


}

/// @nodoc
abstract mixin class _$DpoCopyWith<$Res> implements $DpoCopyWith<$Res> {
  factory _$DpoCopyWith(_Dpo value, $Res Function(_Dpo) _then) = __$DpoCopyWithImpl;
@override @useResult
$Res call({
 bool nominato, String? contatto
});




}
/// @nodoc
class __$DpoCopyWithImpl<$Res>
    implements _$DpoCopyWith<$Res> {
  __$DpoCopyWithImpl(this._self, this._then);

  final _Dpo _self;
  final $Res Function(_Dpo) _then;

/// Create a copy of Dpo
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? nominato = null,Object? contatto = freezed,}) {
  return _then(_Dpo(
nominato: null == nominato ? _self.nominato : nominato // ignore: cast_nullable_to_non_nullable
as bool,contatto: freezed == contatto ? _self.contatto : contatto // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$FornitoreAi {

 String get nome; String? get paese; bool get proprio;
/// Create a copy of FornitoreAi
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$FornitoreAiCopyWith<FornitoreAi> get copyWith => _$FornitoreAiCopyWithImpl<FornitoreAi>(this as FornitoreAi, _$identity);

  /// Serializes this FornitoreAi to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as FornitoreAi;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is FornitoreAi&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.paese, _this.paese) || other.paese == _this.paese)&&(identical(other.proprio, _this.proprio) || other.proprio == _this.proprio));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as FornitoreAi;
  return Object.hash(runtimeType,_this.nome,_this.paese,_this.proprio);
}

@override
String toString() {
  final _this = this as FornitoreAi;
  return 'FornitoreAi(nome: ${_this.nome}, paese: ${_this.paese}, proprio: ${_this.proprio})';
}


}

/// @nodoc
abstract mixin class $FornitoreAiCopyWith<$Res>  {
  factory $FornitoreAiCopyWith(FornitoreAi value, $Res Function(FornitoreAi) _then) = _$FornitoreAiCopyWithImpl;
@useResult
$Res call({
 String nome, String? paese, bool proprio
});




}
/// @nodoc
class _$FornitoreAiCopyWithImpl<$Res>
    implements $FornitoreAiCopyWith<$Res> {
  _$FornitoreAiCopyWithImpl(this._self, this._then);

  final FornitoreAi _self;
  final $Res Function(FornitoreAi) _then;

/// Create a copy of FornitoreAi
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? nome = null,Object? paese = freezed,Object? proprio = null,}) {
  return _then(FornitoreAi(
nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,paese: freezed == paese ? _self.paese : paese // ignore: cast_nullable_to_non_nullable
as String?,proprio: null == proprio ? _self.proprio : proprio // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [FornitoreAi].
extension FornitoreAiPatterns on FornitoreAi {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _FornitoreAi value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _FornitoreAi() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _FornitoreAi value)  $default,){
final _that = this;
switch (_that) {
case _FornitoreAi():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _FornitoreAi value)?  $default,){
final _that = this;
switch (_that) {
case _FornitoreAi() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String nome,  String? paese,  bool proprio)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _FornitoreAi() when $default != null:
return $default(_that.nome,_that.paese,_that.proprio);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String nome,  String? paese,  bool proprio)  $default,) {final _that = this;
switch (_that) {
case _FornitoreAi():
return $default(_that.nome,_that.paese,_that.proprio);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String nome,  String? paese,  bool proprio)?  $default,) {final _that = this;
switch (_that) {
case _FornitoreAi() when $default != null:
return $default(_that.nome,_that.paese,_that.proprio);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _FornitoreAi implements FornitoreAi {
  const _FornitoreAi({required this.nome, this.paese, this.proprio = false});
  factory _FornitoreAi.fromJson(Map<String, dynamic> json) => _$FornitoreAiFromJson(json);

@override final  String nome;
@override final  String? paese;
@override@JsonKey() final  bool proprio;

/// Create a copy of FornitoreAi
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$FornitoreAiCopyWith<_FornitoreAi> get copyWith => __$FornitoreAiCopyWithImpl<_FornitoreAi>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$FornitoreAiToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _FornitoreAi&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.paese, paese) || other.paese == paese)&&(identical(other.proprio, proprio) || other.proprio == proprio));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,nome,paese,proprio);
}

@override
String toString() {
    return 'FornitoreAi(nome: $nome, paese: $paese, proprio: $proprio)';
}


}

/// @nodoc
abstract mixin class _$FornitoreAiCopyWith<$Res> implements $FornitoreAiCopyWith<$Res> {
  factory _$FornitoreAiCopyWith(_FornitoreAi value, $Res Function(_FornitoreAi) _then) = __$FornitoreAiCopyWithImpl;
@override @useResult
$Res call({
 String nome, String? paese, bool proprio
});




}
/// @nodoc
class __$FornitoreAiCopyWithImpl<$Res>
    implements _$FornitoreAiCopyWith<$Res> {
  __$FornitoreAiCopyWithImpl(this._self, this._then);

  final _FornitoreAi _self;
  final $Res Function(_FornitoreAi) _then;

/// Create a copy of FornitoreAi
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? nome = null,Object? paese = freezed,Object? proprio = null,}) {
  return _then(_FornitoreAi(
nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,paese: freezed == paese ? _self.paese : paese // ignore: cast_nullable_to_non_nullable
as String?,proprio: null == proprio ? _self.proprio : proprio // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}


/// @nodoc
mixin _$Titolare {

 String? get nome; String? get indirizzo; String? get codiceFiscale; String? get emailPrivacy; Dpo get dpo; String? get hosting; List<FornitoreAi> get fornitoriAi;
/// Create a copy of Titolare
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$TitolareCopyWith<Titolare> get copyWith => _$TitolareCopyWithImpl<Titolare>(this as Titolare, _$identity);

  /// Serializes this Titolare to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Titolare;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Titolare&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.indirizzo, _this.indirizzo) || other.indirizzo == _this.indirizzo)&&(identical(other.codiceFiscale, _this.codiceFiscale) || other.codiceFiscale == _this.codiceFiscale)&&(identical(other.emailPrivacy, _this.emailPrivacy) || other.emailPrivacy == _this.emailPrivacy)&&(identical(other.dpo, _this.dpo) || other.dpo == _this.dpo)&&(identical(other.hosting, _this.hosting) || other.hosting == _this.hosting)&&const DeepCollectionEquality().equals(other.fornitoriAi, _this.fornitoriAi));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Titolare;
  return Object.hash(runtimeType,_this.nome,_this.indirizzo,_this.codiceFiscale,_this.emailPrivacy,_this.dpo,_this.hosting,const DeepCollectionEquality().hash(_this.fornitoriAi));
}

@override
String toString() {
  final _this = this as Titolare;
  return 'Titolare(nome: ${_this.nome}, indirizzo: ${_this.indirizzo}, codiceFiscale: ${_this.codiceFiscale}, emailPrivacy: ${_this.emailPrivacy}, dpo: ${_this.dpo}, hosting: ${_this.hosting}, fornitoriAi: ${_this.fornitoriAi})';
}


}

/// @nodoc
abstract mixin class $TitolareCopyWith<$Res>  {
  factory $TitolareCopyWith(Titolare value, $Res Function(Titolare) _then) = _$TitolareCopyWithImpl;
@useResult
$Res call({
 String? nome, String? indirizzo, String? codiceFiscale, String? emailPrivacy, Dpo dpo, String? hosting, List<FornitoreAi> fornitoriAi
});


$DpoCopyWith<$Res> get dpo;

}
/// @nodoc
class _$TitolareCopyWithImpl<$Res>
    implements $TitolareCopyWith<$Res> {
  _$TitolareCopyWithImpl(this._self, this._then);

  final Titolare _self;
  final $Res Function(Titolare) _then;

/// Create a copy of Titolare
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? nome = freezed,Object? indirizzo = freezed,Object? codiceFiscale = freezed,Object? emailPrivacy = freezed,Object? dpo = null,Object? hosting = freezed,Object? fornitoriAi = null,}) {
  return _then(Titolare(
nome: freezed == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String?,indirizzo: freezed == indirizzo ? _self.indirizzo : indirizzo // ignore: cast_nullable_to_non_nullable
as String?,codiceFiscale: freezed == codiceFiscale ? _self.codiceFiscale : codiceFiscale // ignore: cast_nullable_to_non_nullable
as String?,emailPrivacy: freezed == emailPrivacy ? _self.emailPrivacy : emailPrivacy // ignore: cast_nullable_to_non_nullable
as String?,dpo: null == dpo ? _self.dpo : dpo // ignore: cast_nullable_to_non_nullable
as Dpo,hosting: freezed == hosting ? _self.hosting : hosting // ignore: cast_nullable_to_non_nullable
as String?,fornitoriAi: null == fornitoriAi ? _self.fornitoriAi : fornitoriAi // ignore: cast_nullable_to_non_nullable
as List<FornitoreAi>,
  ));
}
/// Create a copy of Titolare
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$DpoCopyWith<$Res> get dpo {
  
  return $DpoCopyWith<$Res>(_self.dpo, (value) {
    return _then(_self.copyWith(dpo: value));
  });
}
}


/// Adds pattern-matching-related methods to [Titolare].
extension TitolarePatterns on Titolare {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Titolare value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Titolare() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Titolare value)  $default,){
final _that = this;
switch (_that) {
case _Titolare():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Titolare value)?  $default,){
final _that = this;
switch (_that) {
case _Titolare() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? nome,  String? indirizzo,  String? codiceFiscale,  String? emailPrivacy,  Dpo dpo,  String? hosting,  List<FornitoreAi> fornitoriAi)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Titolare() when $default != null:
return $default(_that.nome,_that.indirizzo,_that.codiceFiscale,_that.emailPrivacy,_that.dpo,_that.hosting,_that.fornitoriAi);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? nome,  String? indirizzo,  String? codiceFiscale,  String? emailPrivacy,  Dpo dpo,  String? hosting,  List<FornitoreAi> fornitoriAi)  $default,) {final _that = this;
switch (_that) {
case _Titolare():
return $default(_that.nome,_that.indirizzo,_that.codiceFiscale,_that.emailPrivacy,_that.dpo,_that.hosting,_that.fornitoriAi);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? nome,  String? indirizzo,  String? codiceFiscale,  String? emailPrivacy,  Dpo dpo,  String? hosting,  List<FornitoreAi> fornitoriAi)?  $default,) {final _that = this;
switch (_that) {
case _Titolare() when $default != null:
return $default(_that.nome,_that.indirizzo,_that.codiceFiscale,_that.emailPrivacy,_that.dpo,_that.hosting,_that.fornitoriAi);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Titolare implements Titolare {
  const _Titolare({this.nome, this.indirizzo, this.codiceFiscale, this.emailPrivacy, this.dpo = const Dpo(), this.hosting,  List<FornitoreAi> fornitoriAi = const <FornitoreAi>[]}): _fornitoriAi = fornitoriAi;
  factory _Titolare.fromJson(Map<String, dynamic> json) => _$TitolareFromJson(json);

@override final  String? nome;
@override final  String? indirizzo;
@override final  String? codiceFiscale;
@override final  String? emailPrivacy;
@override@JsonKey() final  Dpo dpo;
@override final  String? hosting;
 final  List<FornitoreAi> _fornitoriAi;
@override@JsonKey() List<FornitoreAi> get fornitoriAi {
  if (_fornitoriAi is EqualUnmodifiableListView) return _fornitoriAi;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_fornitoriAi);
}


/// Create a copy of Titolare
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$TitolareCopyWith<_Titolare> get copyWith => __$TitolareCopyWithImpl<_Titolare>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$TitolareToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Titolare&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.indirizzo, indirizzo) || other.indirizzo == indirizzo)&&(identical(other.codiceFiscale, codiceFiscale) || other.codiceFiscale == codiceFiscale)&&(identical(other.emailPrivacy, emailPrivacy) || other.emailPrivacy == emailPrivacy)&&(identical(other.dpo, dpo) || other.dpo == dpo)&&(identical(other.hosting, hosting) || other.hosting == hosting)&&const DeepCollectionEquality().equals(other.fornitoriAi, _fornitoriAi));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,nome,indirizzo,codiceFiscale,emailPrivacy,dpo,hosting,const DeepCollectionEquality().hash(_fornitoriAi));
}

@override
String toString() {
    return 'Titolare(nome: $nome, indirizzo: $indirizzo, codiceFiscale: $codiceFiscale, emailPrivacy: $emailPrivacy, dpo: $dpo, hosting: $hosting, fornitoriAi: $fornitoriAi)';
}


}

/// @nodoc
abstract mixin class _$TitolareCopyWith<$Res> implements $TitolareCopyWith<$Res> {
  factory _$TitolareCopyWith(_Titolare value, $Res Function(_Titolare) _then) = __$TitolareCopyWithImpl;
@override @useResult
$Res call({
 String? nome, String? indirizzo, String? codiceFiscale, String? emailPrivacy, Dpo dpo, String? hosting, List<FornitoreAi> fornitoriAi
});


@override $DpoCopyWith<$Res> get dpo;

}
/// @nodoc
class __$TitolareCopyWithImpl<$Res>
    implements _$TitolareCopyWith<$Res> {
  __$TitolareCopyWithImpl(this._self, this._then);

  final _Titolare _self;
  final $Res Function(_Titolare) _then;

/// Create a copy of Titolare
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? nome = freezed,Object? indirizzo = freezed,Object? codiceFiscale = freezed,Object? emailPrivacy = freezed,Object? dpo = null,Object? hosting = freezed,Object? fornitoriAi = null,}) {
  return _then(_Titolare(
nome: freezed == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String?,indirizzo: freezed == indirizzo ? _self.indirizzo : indirizzo // ignore: cast_nullable_to_non_nullable
as String?,codiceFiscale: freezed == codiceFiscale ? _self.codiceFiscale : codiceFiscale // ignore: cast_nullable_to_non_nullable
as String?,emailPrivacy: freezed == emailPrivacy ? _self.emailPrivacy : emailPrivacy // ignore: cast_nullable_to_non_nullable
as String?,dpo: null == dpo ? _self.dpo : dpo // ignore: cast_nullable_to_non_nullable
as Dpo,hosting: freezed == hosting ? _self.hosting : hosting // ignore: cast_nullable_to_non_nullable
as String?,fornitoriAi: null == fornitoriAi ? _self._fornitoriAi : fornitoriAi // ignore: cast_nullable_to_non_nullable
as List<FornitoreAi>,
  ));
}

/// Create a copy of Titolare
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$DpoCopyWith<$Res> get dpo {
  
  return $DpoCopyWith<$Res>(_self.dpo, (value) {
    return _then(_self.copyWith(dpo: value));
  });
}
}

// dart format on
